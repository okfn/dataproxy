import sys
import brewery.dq as dq

transformers = []

def register_transformer(transformer):
    transformers.append(transformer)
    
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

    return info["class"]

def transformer(type_name, flow, url, query):
    """Get transformation module for resource of given type"""
    
    trans_class = find_transformer(extension = type_name)
    if not trans_class:
        raise Exception("No transformer for type '%s'" % type_name)

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

        if "audit" in query:
            self.audit = True
        else:
            self.audit = False

    def read_source_rows(self, src):
        if self.audit:
            stats = {}
            fields = src.field_names
            for field in fields:
                stats[field] = dq.FieldStatistics(field)

        rows = []
        record_count = 0
    
        for row in src.rows():
            rows.append(row)
            if self.audit:
                for i, value in enumerate(row):
                    stats[fields[i]].probe(value)
                    
            record_count += 1
            if self.max_results and record_count >= self.max_results:
                break

        if self.audit:
            audit_dict = {}
            for key, stat in stats.items():
                stat.record_count = record_count
                stat.finalize()
                audit_dict[key] = stat.dict()

        result = {
                    "fields": src.field_names,
                    "data": rows
                  }

        if self.audit:
            result["audit"] = audit_dict

        if self.max_results:
            result["max_results"] = self.max_results

        return result
