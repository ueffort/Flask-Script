# coding=utf-8
"""
adgroup的脚本任务
"""
from flask.ext.script import manager

__author__ = 'GaoJie'
commands = manager.get_commands(__name__)
logger = commands.get_logger()

@commands.command
def cache():
    print 1