# coding=utf-8
import logging
import flask
import re
import os
from settings import *
from flask import Blueprint, _request_ctx_stack
from flask.helpers import get_root_path
from werkzeug.utils import cached_property, import_string

from .exception import AppNotExist, BlueprintNotExist
from .ext.flask_config import FlaskConfig


__author__ = 'GaoJie'
config = FlaskConfig(get_root_path(__name__))
DEBUG = False



def open_debug(b):
    global DEBUG
    DEBUG = b


def create_app(app_name, call_back=None):
    """
    根据AppName来加载app，设定配置信息，初始化app信息
    """
    if app_name not in ALLOW_APP:
        raise AppNotExist(app_name, allow=False)
    try:
        app_obj = __import__(app_name)
        app = getattr(app_obj, 'app')
    except AttributeError as e:
        raise AppNotExist(app_name)
    return call_back(app) if call_back else app


def enter_app_context(app_name):
    """
    根据AppName来加载app，设定配置信息，初始化app信息,返回一个app环境
    """
    if app_name not in ALLOW_APP:
        raise AppNotExist(app_name, allow=False)
    try:
        app_obj = __import__(app_name)
        app = getattr(app_obj, 'app')
    except AttributeError as e:
        raise AppNotExist(app_name)
    return app.app_context()


def init_config():
    global config
    if config.last_obj:
        return
    # 导入生产环境配置
    try:
        config.from_pyfile('../production_settings.py')
    except IOError as e:
        # 导入本地配置
        config.from_pyfile('../local_settings.py')


def init_app(app):
    """
    初始化应用
    :return:
    """
    init_app_config(app)
    init_app_logger(app)
    return app


def init_app_config(app):
    """
    初始化应用配置：对配置信息进行应用划分
    """
    init_config()
    app.config.from_object(config.last_obj)
    if DEBUG:
        app.debug = DEBUG
    config_name = '%s_CONFIG' % app.import_name.upper()
    if config_name not in app.config:
        return False
    app_config = app.config[config_name]
    if type(app_config) not in [dict, tuple]:
        return False
    for key, value in app_config.items():
        app.config[key] = value
    if DEBUG:
        app.debug = DEBUG
    return True


def init_app_logger(app):
    """
    根据配置信息，设定新的logger
    """
    #todo 通过logging的配置文件加载logging，并进行绑定，根据命令行参数切换
    logger = app.logger
    del logger.handlers[:]
    if 'LOGGING_HANDLER' in app.config:
        logging_handler = app.config['LOGGING_HANDLER']
    else:
        logging_handler = 'logging.StreamHandler'
    logging_handler = logging_handler.split('.')
    module = __import__('.'.join(logging_handler[:-1]))
    handler_class = getattr(module, ''.join(logging_handler[-1]))
    arg = app.config['LOGGING_HANDLER_ARG'] if 'LOGGING_HANDLER_ARG' in app.config else {}
    handler = handler_class(*arg)
    log_level = app.config['LOGGING_LEVEL'] if 'LOGGING_LEVEL' in app.config else logging.INFO
    if type(log_level) is str:
        log_level = logging.getLevelName(log_level)
    level = logging.DEBUG if app.debug and log_level >= logging.DEBUG else log_level
    # flask中自定义的logger过滤了非debug设置的所有日志
    logger.setLevel(logging.DEBUG)
    log_format = logging.Formatter(app.config['LOGGING_FORMAT']
                                   if 'LOGGING_FORMAT' in app.config else app.debug_log_format)

    handler.setFormatter(log_format)

    handler.setLevel(level)
    logger.addHandler(handler)
    # 添加异常日志发送email
    if 'LOGGING_EXCEPTION_MAIL' in app.config and not app.debug:
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler(**app.config['LOGGING_EXCEPTION_MAIL'])
        # error == exception
        mail_handler.setLevel(logging.ERROR)
        mail_handler.setFormatter(log_format)
        logger.addHandler(mail_handler)
    return True



def get_module_package(path):
    """
    获取路径下所有模块名
    """
    module_list = []
    package_list = []
    files = os.listdir(path)
    for f in files:
        mat = re.match(r'([^\.]*)(\.py)?$', f)
        if mat and mat.group(1) != '__init__':
            if not mat.group(2):
                package_list.append(mat.group(1))
            elif mat.group(2) == '.py':
                module_list.append(mat.group(1))
    return module_list, package_list


def blueprint_module(module_list, package_full, father_prefix=None, need_lazy=True):
    """
    根据模块列表注册蓝图
    """
    blueprint_map = {}
    if not father_prefix:
        father_prefix = '/'
    else:
        father_prefix = '%s%s/' % (father_prefix, package_full.split('.')[-1])
    func = LazyBlueprint if need_lazy else Blueprint
    if module_list:
        for module_name in module_list:
            blueprint_map[module_name] = func('%s.%s' % (package_full, module_name),
                                              '%s.%s' % (package_full, module_name),
                                              url_prefix='%s%s' % (father_prefix, module_name))
    return blueprint_map, father_prefix


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

def get_current_logger(app, module_full):
    return app.logger.getChild(module_full[len(app.import_name) + 1:])


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
            # print state, endpoint
            return self.redispatch(state, endpoint, **view_args)

        return inner_lazy_load

    @staticmethod
    def redispatch(state, endpoint, **view_args):
        """
        基于flask ：0.10.1
        """
        # print state.app.url_map
        state.app.url_map.update()
        req = _request_ctx_stack.top.request
        adapter = _request_ctx_stack.top.url_adapter
        req.url_rule, req.view_args = adapter.match(return_rule=True)
        rule = req.url_rule
        # print rule, state.app.view_functions
        return state.app.view_functions[rule.endpoint](**req.view_args)
