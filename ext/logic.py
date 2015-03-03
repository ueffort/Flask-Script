# coding=utf-8
import json
from urlparse import urldefrag
import time
from flask.ext.script.exception import ConfigNotExist
from core.model import db, bunny_engine
from core.model.bunny import CreativeAdx
from core.model.bunny_org import CertAudit
from sqlalchemy import text, Integer, String
from flask import current_app

__author__ = 'GaoJie'

if 'DEFAULT_ATTACH_URL' not in current_app.config:
    current_app.logger.exception(ConfigNotExist('DEFAULT_ATTACH_URL', 'Default Domain for Limei DSP '))
default_url = current_app.config['DEFAULT_ATTACH_URL']
# 修正url格式，确保拼接链接正确
if default_url[-1] == '/':
    default_url = default_url[:-1]


class CampaignExt(object):
    @staticmethod
    def quota_ok(campaign):
        """
        判断限额是否还在允许范围
        :param campaign:
        :return:正常返回true，超过返回false
        """
        #展示 点击 预算
        if (campaign.imprQuota == -1 or campaign.imprQuota > campaign.imprConsume)\
                and (campaign.dailyImprQuota == -1 or campaign.dailyImprQuota > campaign.dailyImprConsume) \
                and (campaign.clickQuota == -1 or campaign.clickQuota > campaign.clickConsume)\
                and (campaign.dailyClickQuota == -1 or campaign.dailyClickQuota > campaign.dailyClickConsume) \
                and campaign.budget > campaign.consume \
                and (not campaign.dailyBudget or campaign.dailyBudget > campaign.dailyConsume):
            return True
        return False


class AdgroupExt(object):
    @staticmethod
    def quota_ok(adgroup):
        """
        判断限额是否还在允许范围
        :param adgroup:
        :return:正常返回true，超过返回false
        """
        # 预算 日点击
        if adgroup.inherit_budget == 1:
            return CampaignExt.quota_ok(adgroup.campaign)
        if adgroup.budget > adgroup.consume \
                and (adgroup.dailyClickQuota == -1 or adgroup.dailyClickQuota > adgroup.dailyClickConsume) \
                and adgroup.dailyBudget > adgroup.dailyConsume:
            return True
        return False


class CompanyExt(object):
    @staticmethod
    def attach_url(url, company_id):
        """
        返回对应公司名下的url
        :param url:
        :param company_id:
        :return:
        """
        if not url:
            return None
        if url[0:4] == 'http':
            # 去除锚点,兼容2014-12月之前的
            return urldefrag(url)[0]
        domain = CompanyDomainCache.get_domain(company_id)
        if url[0] == '/':
            url = url[1:]
        if not domain:
            return '%s/%s' % (default_url, url)
        return 'http://%s/upload/%s' % (domain, url)


class AuditExt(object):
    """
    审核操作
    """
    @staticmethod
    def creative(adx, creative, result, reason, status, update_time=True):
        db.session.begin()
        try:
            update_info = {
                "status": status,
                "result": json.dumps(result),
                "auditResult": reason
            }
            if update_time:
                update_info["auditTime"] = int(time.time())
            CreativeAdx.query.filter(CreativeAdx.adxId == adx).filter(CreativeAdx.creativeId == creative.id) \
                .update(update_info)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def customer(adx, customer, result, reason, status, update_time=True, customer_key=False):
        db.session.begin()
        try:
            update_info = {
                "status": status,
                "result": json.dumps(result),
                "auditResult": reason
            }
            if update_time:
                update_info["auditTime"] = int(time.time())
            if customer_key:
                update_info["key"] = customer_key
            CertAudit.query.filter(CertAudit.adxId == adx).filter(CertAudit.certId == customer.id).update(
                update_info)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class CompanyDomainCache(object):
    domain_mapping = {}

    @classmethod
    def get_domain(cls, company_id):
        if company_id not in cls.domain_mapping:
            conn = bunny_engine.connect()
            sql = text("SELECT id, domain FROM b_company_domain WHERE companyId = :company_id") \
                .columns(id=Integer, domain=String).bindparams(company_id=company_id)
            company_domain = conn.execute(sql).fetchone()
            cls.domain_mapping[company_id] = company_domain['domain'] if company_domain else None
        return cls.domain_mapping[company_id]
