"""Data Proxy - XLS transformation adapter"""
import urllib2
import csv

try:
    import json
except ImportError:
    import simplejson as json

def transform(flow, url, query):
    handle = urllib2.urlopen(url)

    reader = csv.reader(handle)

    rows = []
    for row in reader:
        rows.append(row)

    result = {
                "header": {
                    "url": url,
                },
                "response": rows
              }
    
    return result

