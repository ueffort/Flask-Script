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
db = SQLAlchemy(app)
logger = app.logger

from auto import route
