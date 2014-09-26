# coding=utf-8
from random import randint
import string
__author__ = 'GaoJie'


def randstr(str_len=8):
    """
    生成固定长度随机字符串
    :param str_len:
    :return:
    """
    s = ''
    chars = list(string.ascii_letters + string.digits)
    length = len(chars) - 1
    for i in xrange(str_len):
        s += chars[randint(0, length)]
    return s