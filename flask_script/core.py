# coding=utf-8
import argparse
import inspect
from urllib import quote_plus
import sys
from flask import request, current_app, Blueprint
import re
import os
from werkzeug.test import EnvironBuilder, run_wsgi_app

from .decorators import responsed
from .exception import AppNotExist, BlueprintNotExist
from .dispatcher import PathDispatcher
from .framework import init_app, open_debug, create_app, get_current_logger, LazyBlueprint, get_module_package, \
    blueprint_module, get_module_blueprint

__author__ = 'GaoJie'


class Manager(object):
    instance = None

    def __init__(self):
        self._root_package = None
        self._app = None
        self._commands = {}
        self._namespace = {}
        self._package = {}
        self._commands_package = {}
        self.options = None

    def _handle(self, parser):
        parser.add_argument("command", type=str, help="See ReadMe")
        parser.add_argument("-d", action='store_true', default=False, help="Open Debug")
        parser.add_argument("-s", action='store_true', default=False, help="Single Model")
        parser.add_argument("-i", action='store_true', default=False, help="Show Command info")

        self.options, arg = parser.parse_known_args()

        # 是否开启DEBUG模式，会忽略配置中的DEBUG，用于线上调试
        if self.options.d:
            open_debug(True)

        # 减少并发，单模式
        # 如果发现之前的还在执行则停止当前
        basedir = os.path.dirname('./tmp/')
        file_name = '%s/%s' % (basedir, self.options.command.replace('/', '.'))

        if self.options.s:
            if os.path.isfile(file_name):
                print 'Process is running'
                exit()
            if not os.path.exists(basedir):
                os.makedirs(basedir)
            with file(file_name, 'w'):
                os.utime(file_name, None)
        # todo 更改
        param_dict = {}
        for param in arg:
            mat = re.match(r'^--(.*)=(.*)', param)
            if mat and mat.lastindex:
                # 作为可选参数，通过manager.get_param()获取
                param_dict[mat.group(1)] = mat.group(2)
            else:
                # todo 优化参数为函数参数
                pass

        application = PathDispatcher(create_app=create_app)
        builder = EnvironBuilder(path=self.options.command, method='get')

        builder.query_string = '&'.join(
            ["%s=%s" % (quote_plus(key), quote_plus(value)) for key, value in param_dict.items()])

        try:
            run_wsgi_app(application, builder.get_environ())
            if self.options.s:
                os.remove(file_name)
        except AppNotExist as e:
            return e.code
        return 0

    def run(self):
        """
        执行命令行
        :return:
        """
        parser = argparse.ArgumentParser(
            description="Structured call execute scripts, parameters with an optional way to add")
        try:
            result = self._handle(parser)
        except SystemExit as e:
            result = e.code

        sys.exit(result or 0)

    def init_app(self, app, root_package=None):
        """
        初始化当前加载APP信息
        :param app: 传递全局app
        :param root_package: 设定基本根模块
        :return:
        """
        # todo 只允许加载一次
        # todo 创建初始化接口
        self._app = app
        init_app(app)
        self._root_package = root_package = '%s.%s' % (app.import_name, root_package)
        from . import route
        __import__(root_package)

        """
        对request启动后执行，可以操作current_app
        @app.before_first_request
        def import_info():
            app.debug, debug = False, app.debug
            app.debug = debug
        """

    def get_app(self):
        """
        获取app
        :return:
        """
        return self._app

    def add_commands_package(self, path, module_name):
        """
        通过python自身的模块机制加载命令包
        通过懒加载模式，可以将上层模块的加载依次注入blueprint，命令包的前缀自动继承
        :param path:
        :param module_name:
        :return:
        """
        # 获取所有模块名称
        module_list, package_list = get_module_package(path[0])
        self._package[module_name] = (module_list, package_list)
        if module_name == self._root_package:
            father_prefix = None
        else:
            father_prefix = self._namespace[module_name[:module_name.rfind('.')]]
        blueprint_list, father_prefix = blueprint_module(module_list, module_name, father_prefix, True)
        self._namespace[module_name] = father_prefix
        self._commands_package[module_name] = blueprint_list

        # 注册蓝图
        for item in blueprint_list.values():
            self._app.register_blueprint(item)

        # 加载扩展包
        for pa in package_list:
            __import__('%s.%s' % (module_name, pa))

        return blueprint_list, father_prefix

    def get_commands(self, module_name):
        """
        获取当前模块对应的命令集
        :param module_name:
        :return:
        """
        if module_name not in self._commands:
            father_module_name = module_name[:module_name.rfind('.')]
            instance = get_module_blueprint(self._commands_package[father_module_name], module_name)
            self._commands[module_name] = Commands(instance, self)
        return self._commands[module_name]

    def add_commands(self, module_name):
        # todo 单独加载一个python文件作为命令包
        pass

    def add_command(self):
        # todo 单独加载一个fun作为命令
        pass

    def command(self):
        # 修饰符方式加载command
        # todo 单独加载一个fun作为命令
        pass

    @staticmethod
    def get_param(key):
        """
        获取命令行参数
        :param key:
        :return:
        """
        return request.args.get(key)

    @staticmethod
    def get_logger(module_name):
        return get_current_logger(current_app, module_name) if module_name else current_app.logger


class Commands(object):
    def __init__(self, blueprint, manager, module_name=None):
        self._blueprint = blueprint
        self._module_name = module_name
        self.action_list = []
        self.manager = manager

    def route(self, *args, **kwargs):
        action_list = self.action_list
        blueprint = self._blueprint

        def decorator(f):
            action_list.append(kwargs.get("endpoint", f.__name__))
            return blueprint.route(*args, **kwargs)(responsed(f))

        return decorator

    def command(self, f):
        """
        修饰符：添加为command
        :param f:
        :return:
        """
        return Command(self).generate(f)

    def get_logger(self):
        return Manager.get_logger(self._module_name)

    def description(self):
        # todo 处理commands的描述信息
        return self


class Command(object):

    def __init__(self, commands):
        self.commands = commands

    def generate(self, f):
        def proxy(*args, **kwargs):
            param = Param(f)
            if self.commands.manager.options.i:  # 输出help信息
                return param.help()

            return f(*param.args, **param.kwargs) if param.is_ok() else param.error()

        return self.commands.route('/' + f.__name__, endpoint=f.__name__)(proxy)


class Param():
    def __init__(self, f):
        self.f = f
        self.required = []
        self.option = []
        self.args = []
        self.kwargs = {}
        self.parse()

    def parse(self):
        arg = inspect.getargspec(self.f)
        if arg.defaults:
            self.required = arg.args[0:-len(arg.defaults)]
            self.option = arg.args[len(self.required):]
        else:
            self.required = arg.args

    def is_ok(self):
        """
        所有必选参数都需要被设置
        :return:
        """
        if not self.required:
            return True
        for p in self.required:
            a = Manager.get_param(p)
            if a is None:
                return False
            self.args.append(a)
        if not self.option:
            return True
        for p in self.option:
            a = Manager.get_param(p)
            if a is None:
                continue
            self.kwargs[p] = a
        return True

    def error(self):
        if self.required:
            print 'Command need required param: %s' % ','.join(self.required)
        if self.option:
            print '              options param: %s' % ','.join(self.option)
        self.help()

    def help(self):
        """
        直接输出command的说明，后续优化
        :return:
        """
        import locale
        import codecs
        print self.f.__doc__.decode('utf-8').encode(codecs.lookup(locale.getpreferredencoding()).name)