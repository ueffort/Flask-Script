# coding=utf-8
"""
访问调度器：将请求进行逻辑划分
"""

__author__ = 'GaoJie'
from threading import Lock
from werkzeug.wsgi import pop_path_info, peek_path_info


class SubDomainDispatcher(object):
	"""
	子域调度器
	"""
	def __init__(self, domain, create_app):
		self.domain = domain
		self.create_app = create_app
		self.lock = Lock()
		self.instances = {}

	def get_application(self, host):
		host = host.split(':')[0]
		assert host.endswith(self.domain), 'Configuration error'
		sub_domain = host[:-len(self.domain)].rstrip('.')
		with self.lock:
			app = self.instances.get(sub_domain)
			if app is None:
				app = self.create_app(sub_domain)
				self.instances[sub_domain] = app
		return app

	def __call__(self, environ, start_response):
		app = self.get_application(environ['HTTP_HOST'])
		return app(environ, start_response)


class PathDispatcher(object):
	"""
	路径调度器
	"""
	def __init__(self, create_app, default_app=None):
		self.default_app = default_app
		self.create_app = create_app
		self.lock = Lock()
		self.instances = {}

	def get_application(self, prefix):
		with self.lock:
			app = self.instances.get(prefix)
			if app is None:
				app = self.create_app(prefix)
				self.instances[prefix] = app
			return app

	def __call__(self, environ, start_response):
		app = self.get_application(peek_path_info(environ))
		pop_path_info(environ)
		return app(environ, start_response)