# coding=utf-8
from logging import getLogger
import logging
import sys
from common.exception import AppNotExist, BlueprintNotExist
from common.ext.flask_config import FlaskConfig
from flask import Blueprint, g, current_app, Config, _request_ctx_stack
import flask
from flask.helpers import get_root_path
import re
import os
from settings import *
from werkzeug.utils import cached_property, import_string

__author__ = 'GaoJie'
config = FlaskConfig(get_root_path(__name__))


def create_app(app_name):
	"""
	根据AppName来加载app，设定配置信息，初始化app信息
	"""
	global config
	# 导入生产环境配置
	try:
		config.from_pyfile('../production_settings.py')
	except IOError as e:
		#导入本地配置
		config.from_pyfile('../local_settings.py')

	if app_name not in ALLOW_APP:
		raise AppNotExist(app_name, allow=False)
	try:
		app_obj = __import__(app_name)
		app = getattr(app_obj, 'app')
	except (ImportError, AttributeError) as e:
		print e
		raise AppNotExist(app_name)
	return app


def init_app_config(app):
	"""
	初始化应用配置：对配置信息进行应用划分
	"""
	app.config.from_object(config.last_obj)
	config_name = '%s_CONFIG' % app.import_name.upper()
	if config_name not in app.config:
		return False
	app_config = app.config[config_name]
	if type(app_config) not in [dict, tuple]:
		return False
	for key, value in app_config.items():
		app.config[key] = value
	return True


def init_app_logger(app):
	"""
	根据配置信息，设定新的logger
	"""
	#todo 通过logging的配置文件加载logging，并进行绑定，根据命令行参数切换
	logger = app.logger
	if 'LOGGING_HANDLER' in app.config:
		del logger.handlers[:]
		handler_class = __import__(app.config['LOGGING_HANDLER'])
		arg = app.config['LOGGING_HANDLER_ARG'] if 'LOGGING_HANDLER_ARG' in app.config else {}
		handler = handler_class(*arg)
	else:
		handler = logger.handlers[0]
	log_level = app.config['LOGGING_LEVEL'] if 'LOGGING_LEVEL' in app.config else logging.INFO
	if type(log_level) is str:
		log_level = logging.getLevelName(log_level)
	logger.setLevel(logging.DEBUG if app.debug and log_level < logging.DEBUG else log_level)
	log_format = app.config['LOGGING_FORMAT'] if 'LOGGING_FORMAT' in app.config else app.debug_log_format
	handler.setFormatter(logging.Formatter(log_format))
	logger.addHandler(handler)
	return True


def get_module_list(path):
	"""
	获取路径下所有模块名
	"""
	module_list = []
	files = os.listdir(path)
	for f in files:
		mat = re.match(r'(.*)\.py$', f)
		if mat and mat.group(1) != '__init__':
			module_list.append(mat.group(1))
	return module_list


def blueprint_module(app, module_list, alias, need_lazy=True):
	"""
	根据模块列表注册蓝图
	"""
	blueprint_map = {}
	func = LazyBlueprint if need_lazy else Blueprint
	if module_list:
		for module_name in module_list:
			blueprint_map[module_name] = func('%s.%s' % (alias, module_name), '%s.%s.%s' % (app.import_name,
				alias, module_name), url_prefix='/%s' % module_name)
	return blueprint_map


def get_module_blueprint(blueprint_map, module_name):
	"""
	获取模块对应的蓝图
	:param blueprint_map:
	:param module_name:
	:return:
	"""
	module_name = module_name[module_name.rfind('.')+1:]
	if module_name not in blueprint_map:
		raise BlueprintNotExist(module_name)
	return blueprint_map[module_name]


class LazyView(object):
	"""
	延迟加载视图
	LazyView(xx.xxx.view)
	"""
	def __init__(self, import_name):
		self.__module__, self.__name__ = import_name.rsplit('.', 1)
		self.import_name = import_name

	@cached_property
	def view(self):
		return import_string(self.import_name)

	def __call__(self, *args, **kwargs):
		return self.view(*args, **kwargs)


class LazyBlueprint(Blueprint):
	"""
	延迟加载蓝图，一个蓝图对应一个module即可实现
	"""
	def __init__(self, name, import_name, static_folder=None,
	             static_url_path=None, template_folder=None,
	             url_prefix=None, subdomain=None, url_defaults=None):
		super(LazyBlueprint, self).__init__(name, import_name, static_folder,
		                                    static_url_path, template_folder,
		                                    url_prefix, subdomain, url_defaults)
		self.init_lazy = False
		self.states = []
		self.record(self.setup_lazy_load)

	def setup_lazy_load(self, state):
		if not self.init_lazy:
			state.add_url_rule('/<path:endpoint>', '', self.lazy_load_for(state))
			self.states.append(state)

	def lazy_load_for(self, state):
		def inner_lazy_load(endpoint, **view_args):
			if self.init_lazy:
				flask.abort(404)
			self.init_lazy = True
			self.base_functions, self.deferred_functions = self.deferred_functions, []
			__import__(self.import_name)
			state.app.debug, debug = False, state.app.debug
			for fix_state in self.states:
				for deferred in self.deferred_functions:
					deferred(fix_state)
			state.app.debug = debug
			self.deferred_functions = self.base_functions + self.deferred_functions
			return self.redispatch(state, endpoint, **view_args)

		return inner_lazy_load

	@staticmethod
	def redispatch(state, endpoint, **view_args):
		"""
		基于flask ：0.10.1
		"""
		state.app.url_map.update()
		req = _request_ctx_stack.top.request
		adapter = _request_ctx_stack.top.url_adapter
		req.url_rule, req.view_args = adapter.match(return_rule=True)
		rule = req.url_rule
		return state.app.view_functions[rule.endpoint](**req.view_args)
