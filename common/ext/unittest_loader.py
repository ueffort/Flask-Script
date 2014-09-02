from unittest import TestLoader
from common.framework import enter_app_context
from settings import ALLOW_APP

__author__ = 'GaoJie'


class UnittestLoader(TestLoader):
    def loadTestsFromModule(self, module, use_load_tests=True):
        if module.split('.')[0] in ALLOW_APP:
            with enter_app_context(module.split('.')):
                return super(UnittestLoader, self).loadTestsFromModule(module, use_load_tests)
        return super(UnittestLoader, self).loadTestsFromModule(module, use_load_tests)