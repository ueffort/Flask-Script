# coding=utf-8
from flask.ext.mail import Mail, Message

__author__ = 'GaoJie'


def send_email(app, title, content, to_list, cc_list=None, sender=None):
	"""
	发送邮件
	"""
	mail = Mail(app)
	msg = Message(subject=title, body=content, html=True, recipients=to_list, sender=sender)
	if not cc_list:
		msg.cc = cc_list
	mail.send(msg)
