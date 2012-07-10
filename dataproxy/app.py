"""Data Proxy: a google app-engine application for proxying data to json (jsonp) format.

Author: James Gardner <http://jimmyg.org>
Author: Stefan Urbanek <stefan.urbanek@gmail.com>

Transformation modules
======================

For each resource type there should be a module in transform/<type>_transform.py

Each module should implement:
* ``transformer(flow, url, query)``, should return a Transformer subclass
* Transformer subclass with __init__(flow, url, query)

Existing modules:
* transform/csv_transform - CSV files
* transform/xls_transform - Excel XLS files


Random notes
============

Mount point
Maximum file size

http://someproxy.example.org/mount_point?url=url_encoded&sheet=1&range=A1:K3&doc=no&indent=4&format=jsonp

Response format:

header
    url = http://...file.xls
    option = 'row=5&row=7&row_range=10:100000:5000',
response
    sheet = 'Sheet 1',
    data = [
        [...],
        [...],
        [...],
    ]

* Downloading the entire spreadsheet
* Downloading a single sheet (add ``sheet=1`` to the URL)
* Downloading a range in a single sheet (add ``range=A1:K3`` to the URL) [a bit nasty for CSV files but will do I think]
* Choosing a limited set of rows within the sheet (add ``row=5&row=7&row_range=10:100000:5000`` - rowrange format would be give me a row between 10 and 100000 every 5000 rows)


Hurdles
-------
* Some data sets are not in text-based formats => Don't handle them at this stage
* Excel spreadhseets have formatting and different types => Ignore it, turn everything into a string for now
* Some data sets are huge => don't proxy more than 100K of data - up to the user to filter it down if needed
* We don't want to re-download data sets => Need a way to cache data -> storage API
* Some applications might be wildly popular and put strain on the system -> perhaps API keys and rate limiting are needed so that individual apps/feeds can be disabled. How can we have read API keys on data.gov.uk?
"""

import csv
import os
import logging
import httplib
import urlparse
import urllib2
import re

from cgi import FieldStorage
from StringIO import StringIO
try:
    import json
except ImportError:
    import simplejson as json

import sys
import os

def _add_vendor_packages():
    root = os.path.join(os.path.dirname(__file__), 'vendor')
    for vendor_package in os.listdir(root):
        path = os.path.join(root, vendor_package)
        if path in sys.path:
            continue
        sys.path.insert(1, path)
        # m = "adding %s to the sys.path: %s" % (vendor_package, sys.path)

_add_vendor_packages()

import transform

from bn import AttributeDict

log = logging.getLogger(__name__)

def get_resource_length(url, required = False, follow = False):
    """Get length of a resource"""

    parts = urlparse.urlparse(url)

    connection = httplib.HTTPConnection(parts.netloc)

    try:
        connection.request("HEAD", parts.path)
    except Exception, e:
        raise ResourceError("Unable to access resource", "Unable to access resource. Reason: %s" % e)

    res = connection.getresponse()

    headers = {}
    for header, value in res.getheaders():
        headers[header.lower()] = value

    # Redirect?
    if res.status == 302 and follow:
        if "location" not in headers:
            raise ResourceError("Resource moved, but no Location provided by resource server",
                                    'Resource %s moved, but no Location provided by resource server: %s'
                                    % (parts.path, parts.netloc))

        return get_resource_length(headers["location"], required = required, follow = False)


    if 'content-length' in headers:
        length = int(headers['content-length'])
        return length

    if required:
        raise ResourceError("Unable to get content length",
                                'No content-length returned for server: %s path: %s'
                                % (parts.netloc, parts.path))
    return None

def render(**vars):
    return ["<html>\n"
        "<head>"
        "  <title>%(title)s</title>"
        "</head>\n"
        "<body>\n"
        "  <h1>%(title)s</h1>\n"
        "  <p>%(msg)s</p>\n"
        "</body>\n"
        "</html>\n" %vars
    ]

def error(**vars):
    return json.dumps(dict(error=vars), indent=4)

class ProxyError(StandardError):
    def __init__(self, title, message):
        super(ProxyError, self).__init__()
        self.title = title
        self.message = message
        self.error = "Error"

class ResourceError(ProxyError):
    def __init__(self, title, message):
        super(ResourceError, self).__init__(title, message)
        self.error = "Resource Error"

class RequestError(ProxyError):
    def __init__(self, title, message):
        super(RequestError, self).__init__(title, message)
        self.error = "Request Error"

class HTTPResponseMarble(object):
    def __init__(self, *k, **p):
        self.__dict__['status'] = u'200 OK'
        self.__dict__['status_format'] = u'unicode'
        self.__dict__['header_list'] = [dict(name=u'Content-Type', value=u'text/html; charset=utf8')]
        self.__dict__['header_list_format'] = u'unicode'
        self.__dict__['body'] = []
        self.__dict__['body_format'] = u'unicode'

    def __setattr__(self, name, value):
        if name not in self.__dict__:
            raise AttributeError('No such attribute %s'%name)
        self.__dict__[name] = value

class JsonpDataProxy(object):

    def __init__(self, max_length):
        self.max_length = int(max_length)

    def __call__(self, environ, start_response):
        # This is effectively the WSGI app.
        # Fake a pipestack setup so we cna port this code eventually
        flow = AttributeDict()
        flow['app'] = AttributeDict()
        flow['app']['config'] = AttributeDict()
        flow['app']['config']['proxy'] = AttributeDict(max_length=int(self.max_length))
        flow['environ'] = environ
        flow['http_response'] = HTTPResponseMarble()
        flow.http_response.header_list = [dict(name='Content-Type', value='application/javascript')]
        flow['query'] = FieldStorage(environ=flow.environ)

        self.index(flow)

        start_response(
            str(flow.http_response.status),
            [tuple([item['name'], item['value']]) for item in flow.http_response.header_list],
        )
        resp  = ''.join([x.encode('utf-8') for x in flow.http_response.body])
        format = None

        if flow.query.has_key('format'):
            format = flow.query.getfirst('format')

        if not format or format == 'jsonp':
            callback = 'callback'
            if flow.query.has_key('callback'):
                callback = flow.query.getfirst('callback')
            return [callback+'('+resp+')']
        elif format == 'json':
            return [resp]
        else:
            title = 'Unknown reply format'
            msg = 'Reply format %s is not supported, try json or jsonp' % format
            flow.http_response.status = '200 Error %s' % title
            return error(title=title, message=msg)

    def index(self, flow):
        if not flow.query.has_key('url'):
            title = 'url query parameter missing'
            msg = 'Please read the dataproxy API format documentation: http://democracyfarm.org/dataproxy/'
            flow.http_response.status = '200 Error %s'%title
            flow.http_response.body = error(title=title, message=msg)
        else:
            url = flow.query.getfirst('url')

            try:
                self.proxy_query(flow, url, flow.query)
            except ProxyError, e:
                flow.http_response.status = '200 %s %s' % (e.error, e.title)
                flow.http_response.body = error(title=e.title, message=e.message)


    def proxy_query(self, flow, url, query):
        parts = urlparse.urlparse(url)

        # Get resource type - first try to see whether there is type= URL option,
        # if there is not, try to get it from file extension

        if parts.scheme not in ['http', 'https']:
            raise ResourceError('Only HTTP URLs are supported',
                                'Data proxy does not support %s URLs' % parts.scheme)

        resource_type = query.getfirst("type")
        if not resource_type:
            resource_type = os.path.splitext(parts.path)[1]

        if not resource_type:
            raise RequestError('Could not determine the resource type',
                                'If file has no type extension, specify file type in type= option')

        resource_type = re.sub(r'^\.', '', resource_type.lower())

        try:
            transformer = transform.transformer(resource_type, flow, url, query)
        except Exception, e:
            raise RequestError('Resource type not supported',
                                'Transformation of resource of type %s is not supported. Reason: %s'
                                  % (resource_type, e))
        length = get_resource_length(url, transformer.requires_size_limit, follow = True)

        log.debug('The file at %s has length %s', url, length)

        max_length = flow.app.config.proxy.max_length

        if length and transformer.requires_size_limit and length > max_length:
            raise ResourceError('The requested file is too big to proxy',
                                'Requested resource is %s bytes. Size limit is %s. '
                                'If we proxy large files we\'ll use up all our bandwidth'
                                % (length, max_length))

        try:
            result = transformer.transform()
        except Exception, e:
            log.debug('Transformation of %s failed. Reason: %s', url, e)
            raise ResourceError("Data Transformation Error",
                                "Data transformation failed. Reason: %s" % e)
        indent=None

        result["url"] = url
        result["length"] = length

        if query.has_key('indent'):
            indent=int(query.getfirst('indent'))

        flow.http_response.body = json.dumps(result, indent=indent)

if __name__ == '__main__':
    from wsgiref.util import setup_testing_defaults
    from wsgiref.simple_server import make_server

    logging.basicConfig(level=logging.DEBUG)
    httpd = make_server('', 8000, JsonpDataProxy(100000))
    print "Serving on port 8000..."
    httpd.serve_forever()


