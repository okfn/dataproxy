"""Data Proxy - CSV transformation adapter"""
import urllib2
import csv

try:
    import json
except ImportError:
    import simplejson as json

def transform(flow, url, query):
    handle = urllib2.urlopen(url)
    reader = csv.reader(handle)

    try:
        max_results = int(query.getfirst("max-results"))
    except:
        raise ValueError("max-results should be an integer")

    rows = []
    result_count = 0
    for row in reader:
        rows.append(row)
        result_count += 1
        if max_results and result_count >= max_results:
            break

    handle.close

    result = {
                "header": {
                    "url": url,
                },
                "response": rows
              }
    if max_results:
        result["max_results"] = max_results
    
    return result

