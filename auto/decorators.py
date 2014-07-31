# coding=utf-8
from functools import wraps

__author__ = 'GaoJie'


def action(action_list, name=None):
	"""
	加入当前环境执行列表
	name应该和route一致，如果route和fun一致，则为空即可
	"""
	def decorator(f):
		action_list.append(f.__name__ if not name else name)

		def decorated_function(*args, **kwargs):
			return f(*args, **kwargs)
		return decorated_function
	return decorator