from webtest import TestApp
from dataproxy.app import JsonpDataProxy
import re
import json
import os
import sys
from nose.tools import assert_equal

sys.path.insert(1, os.path.join(os.path.dirname(__file__), 'dataproxy'))

class TestDataProxy(object):
    def setup(self):
        """Setup DataProxy tests"""

        # Create application
        self.wsgiapp = JsonpDataProxy(100000)
        self.app = TestApp(self.wsgiapp)

        # Define named requests for easier (re)cofiguration and reuse.
        self.requests = {
                "no_type": "url=http://foo.com/foo",
                 "unknown_type": "url=http://foo.com/foo.undefined",
                 "valid_csv": "url=https://raw.github.com/datasets/cofog/master/data/cofog.csv",
                 "valid_csv_limit": {
                     "url": "https://raw.github.com/datasets/cofog/master/data/cofog.csv",
                            "max-results": 3,
                            "format": "json"
                            },
                 "csv_json": "url=https://raw.github.com/datasets/cofog/master/data/cofog.csv&format=json",
                 "valid_xls": "url=http://oee.nrcan.gc.ca/corporate/statistics/neud/dpa/tablestrends2/id_ca_28_e.xls",
                 "untyped_csv": {
                        "url": "http://openeconomics.net/store/8d7d4770-e1d1-11db-9f7e-00145101c316/data",
                        "type": "csv"
                    },
                 "redirect_csv": "url=http://www.archive.org/download/ckan-cofog/cofog.csv",
                 "valid_tsv": "url=https://raw.github.com/okfn/dataconverters/master/testdata/tsv/simple.tsv"
                }
    def get(self, request_name):
        request = self.requests[request_name]

        if type(request) == str:
            request_str = request
        else:
            pairs = ["%s=%s" % item for item in request.items()]
            request_str = "&".join(pairs)

        result = self.app.get('/?' + request_str)

        return result

    def test_no_params(self):
        res = self.app.get('/')
        assert '"error"' in res, res
        assert 'url query parameter missing' in res, res

    def acceptable_response(self, body):
        return re.search('"data": \[\[.*\]\]', body)

    def test_resource_type_support(self):
        res = self.get("no_type")
        assert 'Could not determine the resource type' in res, res

        res = self.get("unknown_type")
        assert 'Resource type not supported' in res, res

        res = self.get("valid_csv")
        assert 'Resource type not supported' not in res, res

        res = self.get("valid_xls")
        assert 'Resource type not supported' not in res, res

    def test_reply(self):
        res = self.get("valid_csv")
        assert self.acceptable_response(res.body), res
        assert 'callback' in res, res

        res = self.get("valid_xls")
        assert self.acceptable_response(res.body), res

        res = self.get("untyped_csv")
        assert self.acceptable_response(res.body), res

        res = self.get("csv_json")
        assert self.acceptable_response(res.body), res
        assert 'callback' not in res, res
        jres = json.loads(res.body)
        assert 'data' in jres
        assert 'url' in jres

    def test_tsv(self):
        res = self.get("valid_tsv")
        assert self.acceptable_response(res.body), res

    def test_redirect(self):
        res = self.get("redirect_csv")
        assert self.acceptable_response(res.body), res

    def test_data(self):
        res = self.get("valid_csv_limit")
        assert self.acceptable_response(res.body), res
        jres = json.loads(res.body)
        rows = jres["data"]
        assert_equal(len(rows), 3)
