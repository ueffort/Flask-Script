# coding=utf-8
"""
基本任务
"""
from smtplib import SMTPRecipientsRefused
from ext.tools.mail import send_email
from core.model import bunny_engine
from flask import request
from flask.ext.script import manager
from sqlalchemy import text

__author__ = 'GaoJie'
commands = manager.get_commands(__name__)
logger = commands.get_logger()


@commands.command
def send_mail():
    mail_list = get_mail_list()
    for m in mail_list:
        try:
            status = send_email(m['subject'], m['body'], [m['to']],
                                cc_list=[m['cc']] if m['cc'] else [],
                                bcc_list=[m['bcc']] if m['bcc'] else [])
        except SMTPRecipientsRefused as e:
            # 收件人拒绝
            sended_mail(m['id'], status=2)
            logger.exception(e)
        else:
            if status:
                sended_mail(m['id'])
                logger.debug("[ MAIL ] %s send mail Success" % (m['id']))
            else:
                logger.error("[ MAIL ] %s send mail Fail" % (m['id']))


@commands.command
def send_mail_simple():
    try:
        send_email(request.args.get('subject'), request.args.get('body'), [request.args.get('to')])
    except SMTPRecipientsRefused as e:
        logger.exception(e)
        return
    else:
        logger.info("[ MAIL ] %s send mail Success")
        return


def get_mail_list():
    """
    获取邮件发送列表
    :return:
    """
    conn = bunny_engine.connect()
    sql = text("SELECT `id`, `to`, `cc`, `bcc`, `subject`, `body` FROM b_mail WHERE `status` = 1")
    return conn.execute(sql).fetchall()


def sended_mail(mail_id, status=0):
    """
    将邮件设定为已发送
    :param mail_id:
    :return:
    """
    conn = bunny_engine.connect()
    sql = text("UPDATE b_mail SET `status` = :status WHERE `id` = :id ").bindparams(status=status, id=mail_id)
    return conn.execute(sql)