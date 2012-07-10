import sys
from base import *

import csv_transform
import xls_transform

register_transformer({
        "name": "xls",
        "class": xls_transform.XLSTransformer,
        "extensions": ["xls"],
        "mime_types": ["application/excel", "application/vnd.ms-excel"]
    })

register_transformer({
        "name": "csv",
        "class": csv_transform.CSVTransformer,
        "extensions": ["csv", "tsv"],
        "mime_types": ["text/csv", "text/comma-separated-values"]
    })
