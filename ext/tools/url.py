# coding=utf-8
import mimetypes
import urllib
import urllib2
from flask import current_app
__author__ = 'GaoJie'


def url_encode(url):
    """
    url加密
    """
    if isinstance(url, unicode):
        return urllib.quote_plus(url.encode('utf-8'))
    return urllib.quote_plus(url)


def get_mime_type(url):
    """
    获取mimeType
    """
    mime = mimetypes.MimeTypes()
    mime_type = mime.guess_type(url)
    return mime_type[0]


def get_url_content(url, data={}, header={}):
    """
    get方式获取页面信息
    """
    if data:
        if url.find('?') >= 0:
            url += '&'
        else:
            url += '?'
        url += urllib.urlencode(data)
    try:
        current_app.logger.debug('[ URL REQUEST ] %s', url)
        if header:
            current_app.logger.debug('[ URL HEADER ] %s', header)
        request = urllib2.Request(url, headers=header)
        content = urllib2.urlopen(request).read()
        current_app.logger.debug('[ URL RESPONSE ] %s', content)
    except Exception as e:
        current_app.logger.error('[ URL EXCEPTION ] %s', e)
        raise
    return content


def post_url_content(url, data, header={}):
    """
    post方式获取页面信息
    """
    try:
        current_app.logger.debug('[ URL REQUEST ] %s', url)
        if header:
            current_app.logger.debug('[ URL HEADER ] %s', header)
        if data:
            current_app.logger.debug('[ URL DATA ] %s', data)
            if isinstance(data, dict):
                data = urllib.urlencode(data)
        request = urllib2.Request(url, data=data, headers=header)
        content = urllib2.urlopen(request).read()
        current_app.logger.debug('[ URL RESPONSE ] %s', content)
    except Exception as e:
        current_app.logger.error('[ URL EXCEPTION ] %s', e)
        raise
    return content