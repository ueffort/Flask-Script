# coding=utf-8
"""
爱奇艺的脚本任务
"""
from auto import app
from auto.decorators import action
from common.decorators import responsed
from common.framework import get_module_blueprint, get_current_logger
from auto.task.material import blueprint_list

__author__ = 'GaoJie'
instance = get_module_blueprint(blueprint_list, __name__)
logger = get_current_logger(app, __name__)
action_list = []


@action(action_list)
@instance.route('/status')
@responsed
def status():
    """
    审核状态判断
    :return:
    """
    logger.debug('iqiyi test')