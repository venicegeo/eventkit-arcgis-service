# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import json

from django.test import TestCase, Client
from django.utils.encoding import smart_str
from mock import patch

logger = logging.getLogger(__name__)

class TestViews(TestCase):

    def setUp(self):
        pass

    def test_healthcheck(self):
        response = Client().get('/healthcheck')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"Success": true}')

    @patch('eventkit_arcgis_service.views.create_mxd_process')
    def test_mxd_with_mxd_file(self, createMXDProcessMock):
        params = {'gpkg': 'geopackage_filename.gpkg', 'mxd': 'mxd_filename.mxd'}
        response = Client().post('/mxd', json.dumps(params), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, '{"Success": true}')

    def test_mxd_without_gpkg_param(self):
        params = {'mxd': 'mxd_filename.mxd'}
        response = Client().post('/mxd', json.dumps(params), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.content, json.dumps({"error": "Invalid method",
                                                       "message": "This endpoint requires a key called 'gpkg' with a "
                                                                  "path to the gpkg."}))

    @patch('eventkit_arcgis_service.views.create_mxd_process')
    def test_mxd_without_mxd_file(self, createMXDProcessMock):
        params = {'gpkg': 'geopackage_filename.gpkg'}
        response_payload = 'response_payload'
        createMXDProcessMock.return_value = response_payload
        response = Client().post('/mxd', json.dumps(params), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, response_payload)
        self.assertEqual(response['Content-Disposition'],
                         'attachment; filename={}'.format(smart_str('geopackage_filename.mxd')))
        self.assertEqual(response['Content-Length'], str(len(response_payload)))
