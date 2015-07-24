# coding=utf-8
from functools import wraps
import time
from flask import current_app

__author__ = 'GaoJie'


def try_times(times, interval, success=True, default=False):
    """
    尝试次数和间隔时间设定
    """
    times = times if times > 0 else 1

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            t = 0
            while True:
                t += 1
                result = f(*args, **kwargs)
                if success == result:
                    return success
                current_app.logger.debug('[ TOOLS ] %s : %s try %s failure, sleep %s', f.__module__, f.__name__, t, interval)
                if t >= times:
                    break
                time.sleep(interval)
            return default

        return decorated_function
    return decorator