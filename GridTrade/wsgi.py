"""
WSGI config for GridTrade project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""

import os

from trade import utils
from threading import Thread
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GridTrade.settings')

application = get_wsgi_application()

t1 = Thread(target=utils.checktreadpool, args=())
t1.start()

