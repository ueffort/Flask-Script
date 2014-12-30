# coding=utf-8
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'GaoJie'

db = SQLAlchemy(session_options={'autocommit': True, 'autoflush': True})

bunny_engine = db.get_engine(current_app, 'bunny')
