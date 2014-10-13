# coding=utf-8
"""
放置逻辑相关的配置，和执行环境无关，可被实际配置替换
"""

# 允许访问的APP
ALLOW_APP = ['auto']

# 测试的模块
TEST_MODULE = ['auto_test']

# Email设定
MAIL_SERVER = 'xx'
MAIL_PORT = 25
MAIL_USERNAME = ''
MAIL_PASSWORD = ''
MAIL_DEFAULT_SENDER = 'xx<xx@xx.com>'

# 日志定义
LOGGING_FORMAT = '%(asctime)s [%(levelname)s] [%(name)s:%(lineno)s] [%(funcName)s] : %(message)s'
LOGGING_EXCEPTION_MAIL = {
    'mailhost': [MAIL_SERVER, MAIL_PORT],
    'fromaddr': MAIL_DEFAULT_SENDER,
    'toaddrs': [],
    'subject': 'dsp-script:Exception Info Email',
    'credentials': [MAIL_USERNAME, MAIL_PASSWORD]
}