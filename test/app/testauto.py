import os
import tempfile
import unittest
from auto import app

__author__ = 'GaoJie'


class FlaskTestCase(unittest.TestCase):
	def setUp(self):
		self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
		self.app = app.test_client()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(app.config['DATABASE'])

	def test_empty_db(self):
		rv = self.app.get('/creative/cache')
		#assert 'No entries here so far' in rv.data