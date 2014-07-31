# -*- coding: utf-8 -*-
"""
自动化脚本应用
"""
from common.framework import init_app_config, init_app_logger
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'GaoJie'

app = Flask(__name__)
init_app_config(app)
init_app_logger(app)
db = SQLAlchemy(app)
logger = app.logger

from auto import route
