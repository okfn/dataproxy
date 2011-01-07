from webtest import TestApp
from dataproxy.app import JsonpDataProxy
import re

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
                 "valid_csv": "url=http://democracyfarm.org/f/ckan/foo.csv",
                 "valid_xls": "url=http://democracyfarm.org/f/ckan/foo.xls",
                 "untyped_csv": {
                        "url": "http://openeconomics.net/store/8d7d4770-e1d1-11db-9f7e-00145101c316/data",
                        "type": "csv"
                    }
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
        return re.search('"response": \[\[.*\]\]', body)
        
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

        res = self.get("valid_xls")
        assert self.acceptable_response(res.body), res

        res = self.get("untyped_csv")
        assert self.acceptable_response(res.body), res
        