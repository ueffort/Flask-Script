# coding=utf-8
import os
import tempfile
import unittest
from test.auto import *
from core.model.bunny import *
from common.tools import send_email

__author__ = 'GaoJie'


class MaterielTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_empty_db(self):
        creative_list = CampaignCreative.query.join(CreativeAdx) \
            .filter(CreativeAdx.status == 4).filter(CampaignCreative.creativeType == 3).all()
        #rv = self.app.get('/materiel/youku/upload')
        #assert 'No entries here so far' in rv.data