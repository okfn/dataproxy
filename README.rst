Data Proxy
++++++++++

Data Proxy is a web service for converting data resources into structured form such as json.

.. image:: http://packages.python.org/dataproxy/_images/data_proxy.png

Supported resource/file types (``type=`` parameter or file extension):

+--------------------+---------------------------------------------+
| Type               | Description                                 |
+====================+=============================================+
| csv                | Comma separated values text file|           |
+--------------------+---------------------------------------------+
| xls                | Microsoft Excel Spreadsheet     |           |
+--------------------+---------------------------------------------+

Supported reply format (``format=`` parameter) types:

* json
* jsonp (default)


Live Service
++++++++++++

http://jsonpdataproxy.appspot.com/


API Documentation
+++++++++++++++++
   
Use::

    DATA_PROXY_URL?url=...

Parameters
==========

+--------------------+--------------------------------------------+
| Parameter          | Description                                |
+====================+============================================+
| ``url``            | URL of data resource, such as XLS or CSV   |
|                    | file. **This is required**                 |
+--------------------+--------------------------------------------+
| ``type``           | Resource/file type. This overrides         |
|                    | autodetection based on file extension. You |
|                    | should also use this if there is no file   |
|                    | extension in the URL but you know the type |
|                    | of the resource.                           |
+--------------------+--------------------------------------------+
| ``max-results``    | Maximum nuber of results (rows) returned   |
+--------------------+--------------------------------------------+
| ``format``         | Output format. Currently ``json`` and      |
|                    | ``jsonp`` are supported                    |
+--------------------+--------------------------------------------+

XLS Parameters:

+--------------------+--------------------------------------------+
| Parameter          | Description                                |
+====================+============================================+
| ``worksheet``      | Worksheet number                           |
+--------------------+--------------------------------------------+

CSV Parameters:

+--------------------+--------------------------------------------+
| Parameter          | Description                                |
+====================+============================================+
| ``encoding``       | Source character encoding.                 |
+--------------------+--------------------------------------------+
| ``dialect``        | Can be used to change the set of parameters|
|                    | specific to a particular CSV dialect used  |
|                    | to read data out of the file.              |
|                    | By default only ``excel`` and ``excel-tab``|
|                    | are supported.                             |
|                    |                                            |
|                    | More dialects can be added modifying the   |
|                    | source code, with the use of               |
|                    | `csv.register_dialect()`_ .                |
+--------------------+--------------------------------------------+



Get whole file as json::

    DATA_PROXY_URL?url=http://democracyfarm.org/f/ckan/foo.csv&format=json
    
result::

    {
       "response" : [
          [ "name","type","amount" ],
          [ "apple","fruit",10 ],
          [ "bananna","fruit",20 ],
          [ "carrot","vegetable",30 ],
          [ "blueberry","fruit", 40 ],
          [ "potato","vegetable",50 ],
          [ "onion","vegetable",60 ],
          [ "garlic","vegetable",70 ],
          [ "orange","vegetable",80 ]
       ],
       "header" : {
          "url" : "http://democracyfarm.org/f/ckan/foo.csv",
       }
    }


Get only first 3 rows as json::

    DATA_PROXY_URL?url=http://democracyfarm.org/f/ckan/foo.csv&max-results=3&format=json
    
result::

    {
       "response" : [
          [ "name","type","amount" ],
          [ "apple","fruit",10 ],
          [ "bananna","fruit",20 ],
       ],
       "max-results": 3,
       "header" : {
          "url" : "http://democracyfarm.org/f/ckan/foo.csv",
       }
    }

Errors
======

+----------------------------------------+----------------------------------------------------+
| Error                                  | Resolution                                         |
+========================================+====================================================+
| Unknown reply format                   | Specify supported reply ``format`` (json, jsonp)   |
+----------------------------------------+----------------------------------------------------+
| No url= option found                   | Provide obligatory ``url`` parameter               |
+----------------------------------------+----------------------------------------------------+
| Could not determine the file type      | URL file/resource has no known file extension,     |
|                                        | provide file type in ``type`` parameter:           |
|                                        | ``type=csv``                                       |
+----------------------------------------+----------------------------------------------------+
| Resource type not supported            | There is no tranformation module available for     |
|                                        | given resource/file type. Please refer to the list |
|                                        | of supported resource types.                       |
+----------------------------------------+----------------------------------------------------+
| Only http is allowed                   | Only HTTP URL scheme is currently supported. Make  |
|                                        | sure that you are accessing HTTP only or try to    |
|                                        | find HTTP alternative for the resource.            |
+----------------------------------------+----------------------------------------------------+
| Could not fetch file                   | It was not possible to access resource at given URL|
|                                        | Check the URL or resource hosting server.          |
+----------------------------------------+----------------------------------------------------+
| The requested file is too big to proxy | Proxy handles files only within certain size limit.|
|                                        | Use alternative smaller resource if possible.      |
+----------------------------------------+----------------------------------------------------+
| Data transformation error              | An error occured during transformation of resource |
|                                        | to structured data. Please refer to the additional |
|                                        | message to learn what went wrong.                  |
+----------------------------------------+----------------------------------------------------+


Install (Local)
+++++++++++++++

Get the repo::

    git clone https://github.com/okfn/dataproxy

Install the submodules (we use submodules or downloaded libraries rather than
requirements file as we need to deploy to app engine)::

    git submobule init
    git submodule update


Deployment
++++++++++

This is a Python google app engine application. Deploy in the usual way.


.. _csv.register_dialect(): http://docs.python.org/library/csv.html#csv.register_dialect


Developer Notes
+++++++++++++++

Things we could support in future
=================================

* Downloading a range in a single sheet (add ``range=A1:K3`` to the URL) [a bit nasty for CSV files but will do I think]
* Choosing a limited set of rows within the sheet (add ``row=5&row=7&row_range=10:100000:5000`` - rowrange format would be give me a row between 10 and 100000 every 5000 rows)

Possible challenges
===================

* Some data sets are not in text-based formats => Don't handle them at this stage
* Some data sets are huge => don't proxy more than 100K of data - up to the user to filter it down if needed
* Some applications might be wildly popular and put strain on the system -> perhaps API keys and rate limiting are needed so that individual apps/feeds can be disabled.

