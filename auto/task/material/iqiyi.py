# coding=utf-8
"""
爱奇艺的脚本任务
"""

from ext.tools.url import get_url_content, post_url_content
from frontend.logic import AuditExt
from frontend import app
from flask.ext.script import manager
from core.model.bunny import *


__author__ = 'GaoJie'
commands = manager.get_commands(__name__)
logger = commands.get_logger()

IQIYI_API = 'http://220.181.184.220/upload/api'
IQIYI_ADX_ID = app.config['ADX_MAPPING']['iqiyi']


@commands.command
def status():
    """
    审核状态判断
    :return:
    """
    creative_list = CampaignCreative.query.join(CreativeAdx).filter(CreativeAdx.adxId == IQIYI_ADX_ID) \
        .filter(CampaignCreative.c_status == 1).filter(CampaignCreative.a_status == 1) \
        .filter(CreativeAdx.status == 4).all()
    if not creative_list:
        logger.info('[ DB ] No result')
        return
    creative_map = {}
    api = IqiyiExchangeApi()
    try:
        for index, creative in enumerate(creative_list):
            format_template = creative.get_format_template()
            template = format_template['template']
            if 'm_id' not in template['adObject']:
                logger.error('[ DB ] Creative:%s, m_id is empty', creative.id)
                continue
            m_id = template['adObject']['m_id']
            creative_map[str(m_id)] = index
        if not creative_map:
            logger.info('[ DB ] No m_id')
            return
        param = ','.join(creative_map.keys())
        result = api.api(api.CREATIVE).action(api.STATUS).param(param).query()
        if result['code'] is not 0 or 'results' not in result:
            logger.error('[ API ] Iqiyi Call material AUDIT RESULTS API failed! %s', result['code'])
        else:
            for data in result['results']:
                index = creative_map.get(str(data['m_id']))
                handle_audit_result(data, creative_list[index])
    except Exception as e:
        logger.exception(e)
    return


@commands.route('/status_one/<creativeId>')
def status_one(creativeId):
    """
    判断单个状态
    :param creativeId:
    :return:
    """
    creative = CampaignCreative.query.join(CreativeAdx).filter(CampaignCreative.id == int(creativeId))\
        .filter(CreativeAdx.adxId == IQIYI_ADX_ID).filter(CreativeAdx.status == 4).first()
    if not creative:
        logger.info('[ DB ] Creative:%s Inconsistent state', creativeId)
        return
    api = IqiyiExchangeApi()
    try:
        format_template = creative.get_format_template()
        template = format_template['template']
        if 'm_id' not in template['adObject']:
            logger.error('[ DB ] Creative:%, m_id is empty', creative.id)
            return
        m_id = template['adObject']['m_id']
        param = m_id
        result = api.api(api.CREATIVE).action(api.STATUS).param(param).query()
        if result['code'] is not 0:
            logger.error('[ API ] Iqiyi Call material AUDIT RESULT API failed! %s', result['code'])
        else:
            result['m_id'] = m_id
            handle_audit_result(result, creative)
    except Exception as e:
        logger.exception(e)
    return


def handle_audit_result(data, creative):
    if data['status'] == 'COMPLETE':
        db.session.begin()
        format_template = creative.get_format_template()
        template = format_template['template']
        template['adObject']['tv_id'] = data['tv_id']
        creative.set_format_template(format_template)
        db.session.add(creative)
        db.session.commit()
        AuditExt.creative(IQIYI_ADX_ID, creative, data, '', 1)
    elif data['status'] == 'AUDIT_UNPASS':
        AuditExt.creative(IQIYI_ADX_ID, creative, data, data['reason'], 3)
    logger.info('CreativeId:%s, m_id:%s, status:%s', creative.id, data['m_id'], data['status'])


class IqiyiExchangeApi(object):
    # api
    CREATIVE = 'ad'
    # action
    ADD = 0
    UPDATE = 1
    STATUS = 'status'
    STATUS_MAPPING = {
        CREATIVE: 'batchQuery',
    }
    API = {CREATIVE}
    DATA_MAPPING = {
        CREATIVE: {
            ADD: 'm_id',
            UPDATE: False,
            STATUS: 'batch'
        }
    }
    ERROR_MESSAGE = {
        1001: "认证错误",
        4001: "参数错误",
        5001: "服务端错误",
        5002: "执行插入过程中发生了错误",
        5003: "应用请求超过限制",
    }

    def __init__(self):
        self._token = app.config['IQIYI_DSP_TOKEN']
        self._url = ''
        self._action = ''
        self._api = ''
        self._param = {}

        pass

    def api(self, api):
        self._api = api
        return self

    def action(self, action):
        self._action = action
        return self

    def param(self, param):
        if isinstance(param, list):
            self._param = param
        elif isinstance(self._param, list):
            self._param = param
        elif isinstance(param, str):
            self._param = param
        else:
            self._param.update(param)
        return self

    def error(self, error_key):
        return self.ERROR_MESSAGE[int(error_key)] if int(error_key) in self.ERROR_MESSAGE else 'undefined error code'

    def _generate_url(self):
        if self._action == self.STATUS:
            action = self.STATUS_MAPPING[self._api]
        else:
            action = self._action
        self._url = IQIYI_API + '/' + action
        return self

    def query(self):
        self._generate_url()
        if not self._url:
            logger.error("[ API ] Iqiyi Api (url)%s 、(param)%s" % (self._url, self._param))
            return None
        param_data = {
            'dsp_token': self._token
        }
        field_name = self.DATA_MAPPING[self._api][self._action]
        if field_name:
            param_data.update({field_name: self._param})
        else:
            param_data.update(self._param)
        if self._action in [self.ADD, self.UPDATE]:
            response = post_url_content(self._url, param_data)
        elif self._action in [self.STATUS]:
            response = get_url_content(self._url, param_data)
        else:
            logger.error("[ API ERROR ] IQIYI action must POST or GET")
            return False
        result = json.loads(response)
        self._url = ''
        self._action = ''
        self._api = ''
        self._param = {}
        return result