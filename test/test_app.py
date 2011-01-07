from webtest import TestApp
from dataproxy.app import JsonpDataProxy

class TestDataProxy(object):
    def setup(self):
        """Setup DataProxy tests"""
        
        # Create application
        self.wsgiapp = JsonpDataProxy(100000)
        self.app = TestApp(self.wsgiapp) 
        
        # Define named requests for easier (re)cofiguration and reuse.
        self.requests = {"no_type": "url=http://foo.com/foo",
                         "unknown_type": "url=http://foo.com/foo.undefined",
                         "valid_csv": "url=http://democracyfarm.org/f/ckan/foo.csv",
                         "valid_xls": "url=http://democracyfarm.org/f/ckan/foo.xls"}
        
    def get(self, request_name):
        result = self.app.get('/?' + self.requests[request_name])
        return result
        
    def test_no_params(self):
        res = self.app.get('/')
        assert '"error"' in res, res
        assert 'url query parameter missing' in res, res
    def test_no_resource_type(self):
        res = self.get("no_type")
        assert 'Could not determine the resource type' in res, res

        res = self.get("unknown_type")
        assert 'Resource type not supported' in res, res

        res = self.get("valid_csv")
        assert 'Resource type not supported' not in res, res
    

    def test_reply(self):
        pass