# coding=utf-8
from flask import current_app
from flask.ext.mail import Mail, Message

__author__ = 'GaoJie'


def send_email(title, content, to_list, cc_list=None, bcc_list=None, sender=None):
    """
    发送邮件
    """
    mail = Mail(current_app)
    extra = {
        "Accept-Charset": "ISO-8859-1,utf-8"
    }
    msg = Message(subject=title, html=content, recipients=to_list, sender=sender, cc=cc_list, bcc=bcc_list, extra_headers=extra)
    return mail.send(msg)