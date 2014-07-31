# coding=utf-8
"""
creative的脚本任务
"""
from auto.decorators import action
from auto.task import logger as parent_logger
from common.decorators import responsed
from common.framework import get_module_blueprint
from auto.task import task_blueprint

__author__ = 'GaoJie'
task = get_module_blueprint(task_blueprint, __name__)
logger = parent_logger.getChild('creative')

action_list = []


@action(action_list)
@task.route('/cache')
@responsed
def cache():
	logger.debug(12312312)