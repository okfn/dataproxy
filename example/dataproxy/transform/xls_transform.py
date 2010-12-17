"""Data Proxy - XLS transformation adapter"""
import urllib2
import xlrd
try:
    import json
except ImportError:
    import simplejson as json

def transform(flow, url, query):
    handle = urllib2.urlopen(url)
    resource_content = handle.read()
    handle.close()

    sheet_name = ''
    if flow.query.has_key('sheet'):
        sheet_number = int(flow.query.getfirst('sheet'))
    else:
        sheet_number = 0

    book = xlrd.open_workbook('file', file_contents=resource_content, verbosity=0)
    names = []
    for sheet_name in book.sheet_names():
        names.append(sheet_name)
    rows = []
    sheet = book.sheet_by_name(names[sheet_number])
    for rownum in range(sheet.nrows):
        vals = sheet.row_values(rownum)
        rows.append(vals)

    result = {
                "header": {
                    "url": url,
                    "sheet_name": sheet_name,
                    "sheet_number": sheet_number,
                },
                "response": rows
              }
    
    return result

