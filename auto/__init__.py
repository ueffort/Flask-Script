# -*- coding: utf-8 -*-
"""
自动化脚本应用
"""
from flask import Flask
from flask.ext.script import manager
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'GaoJie'

app = Flask(__name__)
manager.init_app(app, 'task')
# 自定义的应用配置信息
db = SQLAlchemy(app, session_options={'autocommit': True, 'autoflush': True})
logger = app.logger
