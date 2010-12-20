from google.appengine.ext.webapp.util import run_wsgi_app
import os
from app import JsonpDataProxy

application = JsonpDataProxy(100000)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
