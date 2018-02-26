from __future__ import absolute_import

from django.core.management import BaseCommand
import os
from waitress import serve

from ...wsgi import application

import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Serves the Eventkit-ArcGIS-service up with the given `host` and `port." \
           "Example: python manage.py serve 0.0.0.0 8000"

    def add_arguments(self, parser):
        parser.add_argument('host', type=str)
        parser.add_argument('port', type=int)

    def handle(self, *args, **options):
        logger.error("LOG_LEVEL set to {0}".format(os.getenv('LOG_LEVEL')))
        serve(application, host=options['host'], port=options['port'])
