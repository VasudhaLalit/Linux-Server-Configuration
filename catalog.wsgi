#!/usr/bin/python3.5
import sys
import os
import logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
sys.path.insert(0,"/var/www/catalog/")
sys.path.append('/var/www/catalog/Catalog')
sys.path.append('/usr/local/lib/python3.5/site-packages')


from Employee import app as application
application.secret_key = 'super'
