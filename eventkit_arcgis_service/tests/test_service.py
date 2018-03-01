# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging
import filecmp

from django.test import TestCase
from eventkit_arcgis_service.service import expand_bbox, get_temp_mxd

logger = logging.getLogger(__name__)

class TestService(TestCase):

    def setUp(self):
        self.sample_gpkg = './data/osm/test-osm-20180301.gpkg'
        self.sample_mxd = 'eventkit_arcgis_service\static\sample_mxd.mxd'

    def test_expand_bbox(self):
        self.assertEquals(expand_bbox([2,34,7,42], [5,20,300,24]), [2,20,300,42])

    def test_get_temp_mxd(self):
        with get_temp_mxd(self.sample_gpkg) as result_mxd_file:
            #self.assertTrue(filecmp.cmp(self.sample_mxd, result_mxd_file, shallow=False))
            with open(self.sample_mxd) as sample:
                with open(result_mxd_file) as result:
                    self.assertEqual(sample.read(), result.read())
