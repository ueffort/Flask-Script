#!evn/bin/python
# -*- coding: utf-8 -*-
import unittest
from urllib import quote_plus
import re
from common.dispatcher import *
from werkzeug.test import EnvironBuilder, run_wsgi_app
from settings import TEST_MODULE

__author__ = 'GaoJie'
import argparse
from common.framework import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Structured call execute scripts, parameters with an optional way to add")
    parser.add_argument("uri", type=str, help="See ReadMe")
    parser.add_argument("--method", type=str, choices=("get", "post", "delete"), default='get', help="Http Method")

    options, arg = parser.parse_known_args()

    # 单元测试
    if options.uri in TEST_MODULE:
        argv = sys.argv[2:]
        argv.insert(0, sys.argv[0])
        unittest.main(module=options.uri, argv=argv)

    application = PathDispatcher(create_app=create_app)

    data_dict = {}
    for param in arg:
        mat = re.match(r'^--(.*)=(.*)', param)
        if mat.lastindex:
            data_dict[mat.group(1)] = mat.group(2)

    builder = EnvironBuilder(path=options.uri, method=options.method, data=data_dict)
    if options.method == 'post':
        builder.content_type = 'application/x-www-form-urlencoded'
    elif options.method == 'get':
        builder.query_string = '&'.join(["%s=%s" % (quote_plus(key), quote_plus(value)) for key, value in data_dict.items()])

    try:
        run_wsgi_app(application, builder.get_environ())
    except AppNotExist as e:
        print e
        exit()
