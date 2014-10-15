# coding=utf-8
from common.exception import ConfigNotExist
from flask import current_app
import redis

__author__ = 'GaoJie'

redis_map = {}


def get(name='default'):
    connect_name = '%s_%s' % (current_app.import_name, name)
    if connect_name in redis_map:
        return redis_map[connect_name]
    config_map = current_app.config.get('REDIS_BINDS')
    try:
        if not config_map or name not in config_map:
            current_app.logger.error('[ CONFIG ] Config key：%s need %s', config_map, name)
            raise ConfigNotExist('REDIS_BINDS', 'need %s' % name)
        redis_map[connect_name] = redis.StrictRedis(**config_map[name])
        return redis_map[connect_name]
    except Exception as e:
        current_app.logger.exception(e)

get_redis = get

