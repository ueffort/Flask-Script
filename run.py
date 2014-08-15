#!env/bin/python
# -*- coding: utf-8 -*-

from auto import app as default_app
from common.dispatcher import *
from common.framework import *


#application = SubdomainDispatcher('limei.com', make_app)

application = PathDispatcher(create_app=create_app, default_app=default_app)
