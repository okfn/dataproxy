import sys

def transformer(type_name, flow, url, query):
    """Get transformation module for resource of given type"""
    module_name = "transform.%s_transform" % type_name
    if module_name in sys.modules:
        module= sys.modules[module_name]
    else:
        __import__(module_name)
        module = sys.modules[module_name]

    return module.transformer(flow, url, query)

class Transformer(object):
    """Data resource transformer - abstract ckass"""
    def __init__(self, flow, url, query):
        self.flow = flow
        self.url = url
        self.query = query

        self.requires_size_limit = True
        
        self.max_results = None
        if "max-results" in query:
            try:
                self.max_results = int(query.getfirst("max-results"))
            except:
                raise ValueError("max-results should be an integer")
        