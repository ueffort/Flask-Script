# coding=utf-8
from auto import app, logger as app_logger
from common.framework import get_module_list, blueprint_module

__author__ = 'GaoJie'
# 获取所有模块名称
all_task = get_module_list(__path__[0])

task_blueprint = blueprint_module(app, all_task, 'task')

logger = app_logger.getChild('task')


