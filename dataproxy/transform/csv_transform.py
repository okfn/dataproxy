"""Data Proxy - CSV transformation adapter"""
import urllib2
import csv
import transform

try:
    import json
except ImportError:
    import simplejson as json

def transformer(flow, url, query):
    return CSVTransformer(flow, url, query)
        
class CSVTransformer(transform.Transformer):
    def __init__(self, flow, url, query):
        super(CSVTransformer, self).__init__(flow, url, query)
        self.requires_size_limit = False
        
    def transform(self):
        handle = urllib2.urlopen(self.url)
        reader = csv.reader(handle)

        rows = []
        result_count = 0
        
        for row in reader:
            rows.append(row)
            result_count += 1
            if self.max_results and result_count >= self.max_results:
                break

        handle.close()

        result = {
                    "header": {
                        "url": self.url,
                    },
                    "response": rows
                  }

        if self.max_results:
            result["max_results"] = self.max_results
    
        return result

