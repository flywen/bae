#-*- coding:utf-8 -*-
import django

def app(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    body=["Welcome to Flywen's blog!\n"]
    #return body
    return 'django is:' + django.get_version()

from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app)
