Data Proxy
++++++++++

Data Proxy is a web service for converting data resources into structured form such as json.

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





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
