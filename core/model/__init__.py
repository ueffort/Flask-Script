# coding=utf-8
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'GaoJie'

db = SQLAlchemy(session_options={'autocommit': True, 'autoflush': True})


def connected(engine):
    conn_map = {}

    def f(**kwargs):
        if not kwargs:
            # 默认参数
            kwargs = {"autocommit": True}
        v = ''.join(["%s%s" % (str(k), str(v)) for k, v in kwargs.items()])
        m5 = hashlib.md5()
        m5.update(v)
        key = m5.hexdigest()
        if key not in conn_map:
            conn_map[key] = engine.connect().execution_options(**kwargs)
        return conn_map[key]
    return f
