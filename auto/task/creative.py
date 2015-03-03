# coding=utf-8
"""
creative的脚本任务
"""
from flask.ext.script import manager

__author__ = 'GaoJie'
commands = manager.get_commands(__name__)
logger = commands.get_logger()


@commands.command
def cache():
    logger.debug(12312312)