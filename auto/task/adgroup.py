# coding=utf-8
"""
adgroup的脚本任务
"""
from auto.decorators import action
from common.decorators import responsed
from common.framework import get_module_blueprint
from auto.task import blueprint_list

__author__ = 'GaoJie'
instance = get_module_blueprint(blueprint_list, __name__)
action_list = []


@action(action_list)
@instance.route('/cache')
@responsed
def cache():
    print 1