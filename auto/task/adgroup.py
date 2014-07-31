# coding=utf-8
"""
adgroup的脚本任务
"""
from common.framework import get_module_blueprint
from auto.task import task_blueprint

__author__ = 'GaoJie'
task = get_module_blueprint(task_blueprint, __name__)


@task.route('/cache')
def cache():
	print 1