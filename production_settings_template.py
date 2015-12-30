# coding=utf-8
from settings import *

DEBUG = False
ENV = 'production'
# 设定AUTO的配置信息
AUTO_CONFIG = {
    'SQLALCHEMY_DATABASE_URI': 'mysql://user:password@server:port/dbname',
	'REDIS_BINDS':{
		'default':{}
	}
}
