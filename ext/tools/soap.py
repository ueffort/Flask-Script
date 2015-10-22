# coding=utf-8
import logging
from flask import current_app
from flask.ext.script.ext._logging import init_logger

__author__ = 'tutu'

logger = logging.getLogger('suds.client')
init_logger(logger)

from suds.client import Client


def register_client(url):
    return Client(url)


def service_method(client, method, *args):
    try:
        method_f = getattr(client.service, method)
        content = method_f(*args)
        current_app.logger.debug('[ SOAP RESPONSE ] %s', content)
    except Exception as e:
        current_app.logger.error('[ SOAP EXCEPTION ] %s', e)
        raise
    return content
