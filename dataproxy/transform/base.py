import sys

transformers = [
    {
        "name": "xls",
        "class": "XLSTransformer",
        "extensions": ["xls"],
        "mime_types": ["application/excel", "application/vnd.ms-excel"]
    },
    {
        "name": "csv",
        "class": "CSVTransformer",
        "extensions": ["csv"],
        "mime_types": ["text/csv", "text/comma-separated-values"]
    }
]

def find_transformer(extension = None, mime_type = None):
    if not extension and not mime_type:
        raise ValueError("Either extension or mime type should be specified")

    info = None
    for trans in transformers:
        if extension and extension in trans["extensions"]:
            info = trans
        if mime_type and mime_type in trans["mime_types"]:
            info = trans
    if not info:
        return None
    
    if "module" in info:
        module_name = info["module"]
    else:
        module_name = "dataproxy.transform.%s_transform" % info["name"]

    if not module_name in sys.modules:
        raise RuntimeError("Module '%s' for transformer type '%s' does not exist" % 
                    (module_name, info["name"]) )

    module = sys.modules[module_name]
    class_name = info["class"]
    
    if not class_name in module.__dict__:
        raise RuntimeError("Class '%s' (in module '%s') for transformer type '%s' does not exist" % 
                    (class_name, module_name, info["name"]) )

    trans_class = module.__dict__[class_name]

    return trans_class

def transformer(type_name, flow, url, query):
    """Get transformation module for resource of given type"""
    
    trans_class = find_transformer(extension = type_name)
    if not trans_class:
        raise Exception("No transofmer for type '%s'" % type_name)

    return trans_class(flow, url, query)

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
