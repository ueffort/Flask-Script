# coding=utf-8
from flask import current_app

__author__ = 'GaoJie'


def init_logger(logger):
    """
    绑定第三方logger使用相同的handler
    :param logger:
    :return:
    """
    logger.setLevel(current_app.logger.level)
    for handler in current_app.logger.handlers:
        logger.addHandler(handler)
