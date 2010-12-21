"""Data Proxy: a google app-engine application for proxying data to json (jsonp) format.

Author: James Gardner <http://jimmyg.org>
Author: Stefan Urbanek <stefan.urbanek@gmail.com>

Transformation modules
======================

For each resource type there should be a module in transform/<type>_transform.py

Each module should implement ``transform(flow, url, query)`` and should return a dictionary
as a result.

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

import transform

from cgi import FieldStorage
from StringIO import StringIO
try:
    import json
except ImportError:
    import simplejson as json

from bn import AttributeDict

log = logging.getLogger(__name__)

def get_resource_length(server, path):
    """Get length of a resource"""
    
    conn = httplib.HTTPConnection(server)
    conn.request("HEAD", path)
    res = conn.getresponse()

    headers = res.getheaders()
    length = None
    for k, v in headers:
        if k.lower() == 'content-length':
            length = v
            break
    if not length:
        raise Exception('No content-length returned for % server %r path'%(server, path))
    return int(length)

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
            return error(title=title, msg=msg)

    def index(self, flow):
        if not flow.query.has_key('url'):
            title = 'No url= option found'
            msg = 'Please read the API format docs'
            flow.http_response.status = '200 Error %s'%title 
            flow.http_response.body = error(title=title, msg=msg)
        else:
            url = flow.query.getfirst('url')
            self.proxy_query(flow, url, flow.query)

    def proxy_query(self, flow, url, query):
        parts = urlparse.urlparse(url)

        # Get resource type - first try to see whether there is type= URL option, 
        # if there is not, try to get it from file extension
        
        resource_type = query.getfirst("type")
        if not resource_type:
            resource_type = os.path.splitext(parts.path)[1]

        if not resource_type:
            title = 'Could not determine the file type'
            msg = 'If file has no type extension, specify file type in type= option'
            flow.http_response.status = '200 Error %s'%title 
            flow.http_response.body = error(title=title, msg=msg)
            return

        resource_type = re.sub(r'^\.', '', resource_type.lower())

        try:
            trans_module = transform.type_transformation_module(resource_type)
        except:
            title = 'Resource type not supported'
            msg = 'Transformation of resource of type %s is not supported' % resource_type
            flow.http_response.status = '200 Error %s' % title 
            flow.http_response.body = error(title=title, msg=msg)
            return

        if parts.scheme != 'http':
            title = 'Only http is allowed'
            msg = 'We do not support %s URLs'%urlparts.scheme
            flow.http_response.status = '200 Error %s'%title 
            flow.http_response.body = error(title=title, msg=msg)
            return
            
        try:
            length = get_resource_length(parts.netloc, parts.path)
        except:
            title = 'Could not fetch file'
            msg = 'Is the URL correct? Does the server exist?'
            flow.http_response.status = '200 Error %s'%title 
            flow.http_response.body = error(title=title, msg=msg)
            return
            
        log.debug('The file at %s has length %s', url, length)
        
        if length is None:
            title = 'The server hosting the file would not tell us its size'
            msg = 'We will not proxy this file because we don\'t know its length'
            flow.http_response.status = '200 Error %s'%title 
            flow.http_response.body = error(title=title, msg=msg)
            return
        elif length > flow.app.config.proxy.max_length:
            title = 'The requested file is too big to proxy'
            msg = 'Sorry, but your file is %s bytes, over our %s byte limit. If we proxy large files we\'ll use up all our bandwidth'%(
                length, 
                flow.app.config.proxy.max_length,
            )
            flow.http_response.status = '200 Error %s'%title 
            flow.http_response.body = error(title=title, msg=msg)
            return
            
        result = trans_module.transform(flow, url, query)

        indent=None

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


