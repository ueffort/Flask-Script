# coding=utf-8
from auto import app
from common.framework import get_module_package, blueprint_module
from auto.task import url_prefix as father_url

__author__ = 'GaoJie'
# 获取所有模块名称
module_list, package_list = get_module_package(__path__[0])

blueprint_list, url_prefix = blueprint_module(module_list, __name__, father_url)

# 注册蓝图
for item in blueprint_list.values():
    app.register_blueprint(item)

# 加载扩展包
for pa in package_list:
    __import__('%s.%s' % (__name__, pa))