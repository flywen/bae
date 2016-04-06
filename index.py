#-*- coding:utf-8 -*-
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flywen.settings")

# from django.core.wsgi import get_wsgi_application
# from bae.core.wsgi import WSGIApplication
# application = WSGIApplication(get_wsgi_application())

from django.core.wsgi import get_wsgi_application
from bae.core.wsgi import WSGIApplication
application = WSGIApplication(get_wsgi_application())