"""Data Proxy - CSV transformation adapter"""
import urllib2
import csv
import base
import brewery.ds as ds

try:
    import json
except ImportError:
    import simplejson as json

class CSVTransformer(base.Transformer):
    def __init__(self, flow, url, query):
        super(CSVTransformer, self).__init__(flow, url, query)
        self.requires_size_limit = False

        if 'encoding' in self.query:
            self.encoding = self.query["encoding"]
        else:
            self.encoding = 'utf-8'

        if 'dialect' in self.query:
            self.dialect = self.query["dialect"]
        else:
            self.dialect = None
        
    def transform(self):
        handle = urllib2.urlopen(self.url)

        src = ds.CSVDataSource(handle, encoding = self.encoding, dialect = self.dialect)
        src.initialize()
        
        result = self.read_source_rows(src)
        handle.close()
        
        return result

