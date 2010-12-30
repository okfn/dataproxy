"""Data Proxy - XLS transformation adapter"""
import urllib2
import xlrd
import transform

try:
    import json
except ImportError:
    import simplejson as json

requires_size_limit = True

def transformer(flow, url, query):
    return XLSTransformer(flow, url, query)
        
class XLSTransformer(transform.Transformer):
    def __init__(self, flow, url, query):
        super(XLSTransformer, self).__init__(flow, url, query)

        if 'worksheet' in self.query:
            self.sheet_number = int(self.query.getfirst('worksheet'))
        else:
            self.sheet_number = 0
        
    def transform(self):
        handle = urllib2.urlopen(self.url)
        resource_content = handle.read()
        handle.close()

        sheet_name = ''

        book = xlrd.open_workbook('file', file_contents=resource_content, verbosity=0)
        names = []
        for sheet_name in book.sheet_names():
            names.append(sheet_name)
        rows = []
        sheet = book.sheet_by_name(names[self.sheet_number])

        # Get the rows
        result_count = 0
        for rownum in range(sheet.nrows):
            vals = sheet.row_values(rownum)
            rows.append(vals)
            result_count += 1
            if self.max_results and result_count >= self.max_results:
                break

        result = {
                    "header": {
                        "url": self.url,
                        "worksheet_name": sheet_name,
                        "worksheet_number": self.sheet_number,
                    },
                    "response": rows
                  }
        if self.max_results:
            result["max_results"] = self.max_results
    
        return result

