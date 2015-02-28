# coding=utf-8
import sys
from flask import request
from .decorators import responsed
from .core import Manager

__author__ = 'GaoJie'

current_app = Manager.instance.get_app()


@current_app.route('/test', methods=['post', 'get'])
@responsed
def test():
    if request.method == 'post':
        print 'Post:', request.form
    elif request.method == 'get':
        print 'Get:', request.args


@current_app.errorhandler(404)
@responsed
def choose_task_404(e):
    def tips_module(package_module, package_name, module_name=None):
        try:
            module_list, package_list = Manager.instance._package[package_module.__name__]
        except AttributeError as e:
            print 'No Define Module List and Package List'
            return False, []
        allow_list = module_list + package_list
        if module_name not in allow_list:
            if len(module_list) > 0:
                print '%s List: %s' % (package_name.capitalize(), ' , '.join(module_list))
            if len(package_list) > 0:
                print '%s Package: %s' % (package_name.capitalize(), ' , '.join(package_list))
            return False, []
        return True, package_list

    def tips_import(current_module_full, model_name, action_name):
        try:
            __import__(current_module_full)
        except ImportError as e:
            print '%s(%s) is allowed, but does not exist!' % (model_name.capitalize(), action_name)
            return False
        print '%s: %s ' % (model_name.capitalize(), action_name)
        return sys.modules[current_module_full]

    def tips_action(current_module, action_name=None):
        try:
            # 需在每个模块中添加commands，用于判断可以执行的
            commands = Manager.instance.get_commands(current_module.__name__)
        except AttributeError as e:
            print 'No Define Action List'
            return False
        action_list = commands.action_list
        if action_name not in action_list:
            print 'Action List: %s ' % [value for value in action_list]
            return False
        else:
            print 'Action %s not execute' % action_name
            return False

    path_list = request.path[1:].split('/')
    root_package = Manager.instance._root_package
    model = root_package[root_package.rfind('.') + 1:]
    current_module = sys.modules[root_package]
    package = True
    path_list = [path for path in path_list if path]
    result = False
    # print path_list
    if len(path_list) > 0:
        for index, path in enumerate(path_list):
            root_package = '%s.%s' % (root_package, path)
            parent_module = current_module
            if package:
                result, package_list = tips_module(parent_module, model, path)
            else:
                # print path
                result = tips_action(parent_module, path)
                break
            if not result:
                break
            current_module = tips_import(root_package, model, path)
            package = True if path in package_list else False
            model = path
        if result:
            if package:
                tips_module(current_module, model)
            else:
                tips_action(current_module)
    else:
        tips_module(current_module, model)

# app.add_url_rule('/index', view_func=index)