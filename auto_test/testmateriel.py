# coding=utf-8
import unittest

from . import *
from flask.ext.script import manager


__author__ = 'GaoJie'


class MaterielTestCase(unittest.TestCase):
    """
    不能在调用route的页面测试，需分开测试route中的函数
    """
    def test_iqiyi(self):
        """
        测试iqiyi
        :return:
        """
        client = app.test_client()
        client.get('/materiel/iqiyi/status')
        client.get('/materiel/iqiyi/status_one/18113')

    def test_youku(self):
        """
        测试iqiyi
        :return:
        """
        client = app.test_client()
        client.get('/materiel/youku/status')
        client.get('/materiel/youku/status_one/18055')

    def test_doubleclick(self):
        """
        测试doubleclick
        :return:
        """
        client = app.test_client()
        client.get('/materiel/doubleclick/status')
        client.get('/materiel/doubleclick/status_one/18055')