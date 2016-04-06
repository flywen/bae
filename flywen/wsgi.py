"""
WSGI config for flywen project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flywen.settings")

if 'SERVER_SOFTWARE' in os.environ:
    from django.core.handlers.wsgi import WSGIHandler
    from bae.core.wsgi import WSGIApplication
#     from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(WSGIHandler())
else:
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
