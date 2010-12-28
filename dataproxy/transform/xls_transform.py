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

    try:
        max_results = int(query.getfirst("max-results"))
    except:
        raise ValueError("max-results should be an integer")

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

    # Get the rows
    result_count = 0
    for rownum in range(sheet.nrows):
        vals = sheet.row_values(rownum)
        rows.append(vals)
        result_count += 1
        if max_results and result_count >= max_results:
            break

    result = {
                "header": {
                    "url": url,
                    "sheet_name": sheet_name,
                    "sheet_number": sheet_number,
                },
                "response": rows
              }
    if max_results:
        result["max_results"] = max_results
    
    return result

