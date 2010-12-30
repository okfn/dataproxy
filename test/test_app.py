from webtest import TestApp
from dataproxy.app import JsonpDataProxy

class TestDataProxy:
    def test_01(self):
        ourapp = JsonpDataProxy(100000)
        testapp = TestApp(ourapp)
        res = testapp.get('/')
        assert '"error"' in res, res
        assert 'url query parameter missing' in res, res

