Installation Guide.

- Install Python.
- Install Apache and mod_wsgi.
- Get your database running.
- Remove any old versions of Django.
- Install the Django code. Installing an official release with pip. Installing a distribution-specific package. Installing the development version.

The following files are core working files for the migration:

1)  jquery.js - Which perform HTTP POST request to the Django server to perform a particular operation. 

2)  urls.py - This file is used to map an url to one particular functionality of project. 
    For example : "convert/done" url is mapped to convert method present in signups/views folder.
    You can use this file to refer which url is mapped to which method.
    
3)  template - folder has all the HTML files needed (self-explanatory).
4)  # MOST IMPORTANT FILE:
    views.py -  It holds all the operations (Performing ETL on SQL database to No-SQL database, view SQL data, download transformed database).
