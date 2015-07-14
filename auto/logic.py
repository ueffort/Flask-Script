# coding=utf-8
import json
from urlparse import urldefrag
import time
from core.model import db
from flask.ext.script.exception import ConfigNotExist
from core.model.bunny import bunny_engine, CreativeAdx, CertAudit, Campaign, CampaignAdgroup
from frontend import app
from sqlalchemy import text, Integer, String
from flask import current_app

__author__ = 'GaoJie'

if 'DEFAULT_ATTACH_URL' not in current_app.config:
    current_app.logger.exception(ConfigNotExist('DEFAULT_ATTACH_URL', 'Default Domain for Limei DSP '))
default_url = current_app.config['DEFAULT_ATTACH_URL']
# 修正url格式，确保拼接链接正确
if default_url[-1] == '/':
    default_url = default_url[:-1]
TIMESTAMP = int(time.time())


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

    @staticmethod
    def date_ok(campaign):
        """
        判断排期是否有效
        :param campaign:
        :return:
        """
        if campaign.startDate < TIMESTAMP and (campaign.endDate > TIMESTAMP or campaign.endDate == 0):
            return True
        return False

    @staticmethod
    def status_ok_list():
        """
        获取可投campaign
        :return:
        """
        return Campaign.query.filter(Campaign.status == 1) \
            .filter((Campaign.startDate < TIMESTAMP) & ((Campaign.endDate > TIMESTAMP) | (Campaign.endDate == 0))).all()


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
                and (not adgroup.dailyBudget or adgroup.dailyBudget > adgroup.dailyConsume):
            return True
        return False

    @staticmethod
    def date_ok(adgroup):
        """
        判断排期是否有效
        :param adgroup:
        :return:
        """
        if adgroup.inherit_dayPart == 1:
            return CampaignExt.date_ok(adgroup.campaign)
        if adgroup.startDate < TIMESTAMP and (adgroup.endDate > TIMESTAMP or adgroup.endDate == 0):
            return True
        return False

    @staticmethod
    def status_ok_list():
        """
        获取可投adgroup
        :return:
        """
        return CampaignAdgroup.query.filter(
            ((CampaignAdgroup.c_status == 1) & (CampaignAdgroup.status == 1)) | (CampaignAdgroup.count > 0)).all()


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


class CreativeExt(object):
    @classmethod
    def adx_map(cls, creative):
        # 查询所有支持的adx
        # 百度支持先投放，所以需选择状态4
        # 谷歌需要人工审核，所需需选择状态5
        adx_list = CreativeAdx.query.filter(CreativeAdx.creativeId == creative.id) \
            .filter(CreativeAdx.status.in_([1, 4, 5])) \
            .filter(CreativeAdx.enableStatus == 1) \
            .filter(CreativeAdx.adxId > 0).all()
        l = {}
        for adx in adx_list:
            ok = False
            if adx.status == 1:
                ok = True
            if adx.adxId == app.config['ADX_MAPPING']['baidu'] and adx.status in [1, 4]:
                # 百度的先投放后审核，只考虑广告主状态
                org_cert_id = creative.adgroup.orgCertId
                cert_status = CertAudit.query.filter(CertAudit.certId == org_cert_id) \
                    .filter(CertAudit.adxId == app.config['ADX_MAPPING']['baidu']) \
                    .filter(CertAudit.status == 1).first()
                if cert_status:
                    ok = True
            elif adx.adxId == app.config['ADX_MAPPING']['doubleclick'] and adx.status in [1, 5]:
                # 谷歌判断人工审核状态
                ok = True
            elif adx.adxId == app.config['ADX_MAPPING']['toutiao'] and adx.status in [1, 4]:
                # 今日头条，先投后审
                ok = True
            if ok:
                l[adx.adxId] = adx.status
        return l


class AdxExt(object):
    """
    adx操作
    """
    creative_type_mapping = {}
    trade_mapping = {}

    @classmethod
    def creative_type(cls, adx_id):
        if adx_id not in cls.creative_type_mapping:
            conn = bunny_engine.connect()
            sql = text("SELECT creativeTypeId FROM b_relation_adxCreativeTemplate WHERE adxId = :adx_id")\
                .bindparams(adx_id=adx_id)
            id_list = conn.execute(sql).fetchall()
            cls.creative_type_mapping[adx_id] = [row['creativeTypeId'] for row in id_list] if id_list else []
        return cls.creative_type_mapping[adx_id]

    @classmethod
    def get_trade_id(cls, adx_id, campaign):
        """
        获取行业Id
        :return:
        """
        if adx_id not in cls.trade_mapping:
            conn = bunny_engine.connect()
            sql = text("SELECT m.adproductId, t.adxAdproductId "
                       "FROM b_base_adx_adproduct t "
                       "LEFT JOIN b_base_adproduct_mapping m on t.id = m.adxAdproductId "
                       "WHERE t.adxId = :adx_id").bindparams(adx_id=adx_id)
            result = conn.execute(sql).fetchall()
            if not result:
                current_app.logger.debug('[ DB ] category is empty')
                return {}
            cls.trade_mapping[adx_id] = {}
            for row in result:
                cls.trade_mapping[adx_id][row['adproductId']] = row['adxAdproductId']
        category_id = campaign.categoryId
        if category_id in cls.trade_mapping[adx_id]:
            return cls.trade_mapping[adx_id][category_id]
        else:
            current_app.logger.error(
                '[ DB ] Creative(%s) has no tradeId(%s), Campaign categoryId(%s) not in mapping',
                adx_id, creative.id, category_id)
            return False


class OrgExt(object):
    ALLOW_Q = ['business', 'icp', 'other']

    @classmethod
    def qualifications(cls, org, companyId, accept=['business', 'icp'], name_field='name', file_field='file_url'):
        file_list = []
        if not accept:
            accept = cls.ALLOW_Q
        else:
            accept = set(accept).intersection(cls.ALLOW_Q)
        if 'business' in accept and org.businessLicense:
            file_list.append({
                name_field: "营业执照",
                file_field: CompanyExt.attach_url(org.businessLicense, companyId)
            })
        if 'icp' in accept and org.icp:
            file_list.append({
                name_field: "ICP",
                file_field: CompanyExt.attach_url(org.icp, companyId)
            })
        if 'other' in accept and org.special:
            special = json.loads(org.special)
            if special:
                for k, f in enumerate(special):
                    file_list.append({
                        name_field: "special%s" % str(k+1),
                        file_field: CompanyExt.attach_url(f, companyId)
                    })
        return file_list


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
