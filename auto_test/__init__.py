# coding=utf-8
# 调用应用环境，test中避免调用其他app的环境
from flask.ext.script.framework import enter_app_context

__author__ = 'GaoJie'

enter_app_context('auto').push()
from auto import *