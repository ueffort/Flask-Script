# coding=utf-8
from settings import *
__author__ = 'GaoJie'


class AppNotExist(BaseException):
    """
    app不存在
    """
    def __init__(self, app_name, allow=True):
        self.app_name = app_name
        self.allow = allow

    def __str__(self):
        if self.allow:
            return 'App(%s) is allowed, but does not exist!' % self.app_name
        else:
            return 'App List: %s or Test: %s' % (' , '.join(ALLOW_APP), ' , '.join(TEST_MODULE))


class BlueprintNotExist(BaseException):
    """
    app不存在
    """
    def __init__(self, module_name):
        self.module_name = module_name

    def __str__(self):
        return 'Blueprint Not Initialized : %s ' % self.module_name


class ConfigNotExist(BaseException):
    """
    配置不存在
    """
    def __init__(self, config_key, description):
        self.config_key = config_key
        self.description = description

    def __str__(self):
        return 'Config Not set : %s %s' % (self.config_key, self.description)