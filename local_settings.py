# coding=utf-8
from settings import *

DEBUG = True

# 设定AUTO的配置信息
AUTO_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'mysql://user:password@server:port/dbname',
	'REDIS_BINDS':{
		'default':{
			'host': '127.0.0.1', 'port': 6379
		}
	}
}