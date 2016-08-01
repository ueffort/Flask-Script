# -*- coding: utf8 -*-

import sys
import hashlib
import random
import argparse
import json
import urllib
import urllib2
import time
import copy

from flask import current_app
from flask.ext.script.exception import ConfigNotExist
from frontend import logger


class ElasticSearch(object):
    _host = 'localhost'
    _port = 9200
    _index = None
    _type = None
    DELETE = 'DELETE'
    PUT = 'PUT'
    GET = 'GET'
    POST = 'POST'
    ALL = '_all'

    @classmethod
    def instance(cls, host, port):
        return cls().host(host).port(port)

    def host(self, host):
        self._host = host
        return self

    def port(self, port):
        self._port = port
        return self

    def index(self, index):
        self._index = index
        return self

    def type(self, type):
        self._type = type
        return self

    def delete(self, id=None, data=None):
        if data:
            self.handle(self.DELETE, '_query', data)
        else:
            self.handle(self.DELETE, id)

    def add(self, data, id=None,):
        self.handle(self.POST, id, data)

    def search(self, data, suffix=None):
        return self.handle(self.GET, suffix, data)

    def mapping_type(self, data):
        type = self._type
        self.type(None).handle(self.PUT, '_mapping/%s' % type, {type: data})
        self.type(type)

    def handle(self, method, suffix=None, data=None):
        url = 'http://%s:%s' % (self._host, self._port)
        if self._index:
            url = '%s/%s' % (url, self._index)
            if self._type:
                url = '%s/%s' % (url, self._type)
        if suffix:
            url = '%s/%s' % (url, suffix)
        if isinstance(data, dict):
            data = json.dumps(data)
        logger.debug("[ REQUEST ] %s %s" % (url, data))
        request = urllib2.Request(url, data=data)
        request.get_method = lambda: method
        try:
            response = urllib2.urlopen(request)
            result = response.read()
            logger.debug("[ Response ] %s" % result)
            return json.loads(result)
        except urllib2.URLError as e:
            logger.exception(e)
            return None


class BuildIndex(object):
    def __init__(self, doc_file, date, index, type, config, delimiter, instance=None):
        self.doc_file = doc_file
        time_tuple = time.strptime(date, "%Y-%m-%d")
        timestamp = int(time.mktime(time_tuple))
        self.timestamp = timestamp
        self.index = index
        self.type = type
        self.config = config
        self.delimiter = delimiter
        self.set_instance(instance)

    def set_instance(self, instance):
        self.instance = instance
        self.instance.index(self.index).type(self.type)
        return self

    def delete_date_index(self):
        self.instance.delete(data={
            "query": {
                "range": {"timestamp": {"gte": self.timestamp, "lte": self.timestamp}}
            }
        })

    def rebuild_index(self):
        f = file(self.doc_file)
        field_mapping = {}
        for field in self.config:
            field_mapping[field[0]] = {'type': field[1]}
            # 对字符串不进行分词处理
            if field[1] == 'string':
                field_mapping[field[0]]['index'] = 'not_analyzed'
        self.instance.mapping_type({
            "properties": field_mapping
        })
        for line in f.xreadlines():
            info = line.strip().split(self.delimiter)
            data = {}
            for key, field in enumerate(self.config):
                data[field[0]] = field[2](info[key]) if type(field[2]) == type else self[field[2]]
            self.instance.add(data)
        self.instance.type(None).handle(ElasticSearch.POST, '_flush')

    def __getitem__(self, name):
        if name == 'timestamp':
            return self.timestamp
        return None


class SearchIndex(object):
    SUM = 'sum'
    CREATIVE = 'creative_id'
    ADGROUP = 'adgroup_id'
    CAMPAIGN = 'campaign_id'

    def __init__(self, index, type, instance=None):
        self.index = index
        self.type = type
        self.filter_must_list = []
        self.filter_must_not_list = []
        self.group_list = []
        self.set_instance(instance)

    def set_instance(self, instance):
        self.instance = instance
        return self

    def filter(self, condition, is_must=1):
        if is_must:
            self.filter_must_list.append(condition)
        else:
            self.filter_must_not_list.append(condition)
        return self

    def between(self, start_time, end_time, is_must=1, field='timestamp'):
        condition = {
            "range": {field: {"gte": start_time, "lte": end_time}}
        }
        return self.filter(condition, is_must)

    def filter_id(self, id, id_type, is_must=1):
        condition = {
            "range": {id_type: {"from": id, "to": id}}
        }
        return self.filter(condition, is_must)

    def group_field(self, *args):
        for field in args:
            self.group_list.insert(0, field)
        return self

    def count(self, query=None, clear=True):
        if not query:
            query = self._generate()
        if clear:
            self._clear()
        result = self.instance.index(self.index).type(self.type).handle(ElasticSearch.POST, data=query, suffix="_count")
        return result['count']

    def all(self, query=None):
        data = []
        if not query:
            query = self._generate()
        count = self.count(query=query, clear=False)
        self._clear()
        if not count:
            return data
        query['size'] = count
        result = self.instance.index(self.index).type(self.type).handle(ElasticSearch.POST, data=query, suffix="_search")

        if result:
            result = result['hits']['hits']
            for row in result:
                data.append(self._format(row))
        return data

    def group(self, agg_type, field, query=None):
        data = []
        if not query:
            query = self._generate()
        aggs = {field: {agg_type: {'field': field}}}
        field_list = [field]
        if self.group_list:
            for g_field in self.group_list:
                aggs = {g_field: {'terms': {'field': g_field, 'size': 1000}, 'aggs': aggs}}
                field_list.insert(0, g_field)
        query['aggs'] = aggs
        self._clear()
        result = self.instance.index(self.index).type(self.type).handle(ElasticSearch.POST, data=query, suffix="_search")

        if result:
            result = result["aggregations"]
            data = self._format_group(result, field_list)
        return data

    @staticmethod
    def _format(hit):
        return hit["_source"]

    @classmethod
    def _format_group(cls, aggregations, field_list):
        if len(field_list) == 0:
            return []
        field = field_list[0]
        if field not in aggregations:
            return []
        info = aggregations[field]
        if 'value' in info:
            return {field: info['value']}
        field_list.pop(0)
        data = []
        for item in info['buckets']:
            field_l = [row for row in field_list]
            l = cls._format_group(item, field_l)
            if type(l) == list and len(l) > 0:
                for other in l:
                    other[field] = item['key']
                    data.append(other)
            elif l:
                l[field] = item['key']
                data.append(l)
            else:
                data.append({field: item['key']})
        return data

    def _clear(self):
        self.filter_must_list = []
        self.filter_must_not_list = []
        self.group_list = []

    def _generate(self):
        return {
            "query": {
                "bool": {
                    "must": self.filter_must_list,
                    "must_not": self.filter_must_not_list
                }
            }
        }

elastic_search_map = {}


def get(name='default'):
    connect_name = '%s_%s' % (current_app.import_name, name)
    if connect_name in elastic_search_map:
        return elastic_search_map[connect_name]
    config_map = current_app.config.get('ELASTIC_SEARCH_BINDS')
    try:
        if not config_map or name not in config_map:
            current_app.logger.error('[ CONFIG ] Config key：%s need %s', config_map, name)
            raise ConfigNotExist('ELASTIC_SEARCH_BINDS', 'need %s' % name)
        elastic_search_map[connect_name] = ElasticSearch.instance(**config_map[name])
        return elastic_search_map[connect_name]
    except Exception as e:
        current_app.logger.exception(e)

get_elastic_search = get

if __name__ == '__main__':

    TYPE_MAP = {
        'event': [
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'app': [
            ['app_id', 'string', str],
            ['app_name', 'string', str],
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'geo': [
            ['geo_id', 'long', int],
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'adx': [
            ['adx_id', 'long', int],
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'os': [
            ['os_id', 'long', int],
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'device_type': [
            ['device_type_id', 'long', int],
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'url': [
            ['url', 'string', str],
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ],
        'uv': [
            ['creative_id', 'long', int],
            ['adgroup_id', 'long', int],
            ['campaign_id', 'long', int],
            ['company_id', 'long', int],
            ['event', 'string', str],
            ['count', 'long', int],
            ['timestamp', 'long', 'timestamp']
        ]
    }

    parser = argparse.ArgumentParser(description="Build index of ElasticSearch")
    parser.add_argument("--docs", type=str, help="Docs Data File")
    parser.add_argument("--date", type=str, help="Index Date")
    parser.add_argument("--index", type=str, help="Index name")
    parser.add_argument("--type", type=str, help="Index type")
    parser.add_argument("--delimiter", type=str, default='|', help="line delimiter of File")
    parser.add_argument("--host", type=str, default="localhost", help="ElasticSearch Host")
    parser.add_argument("--port", type=str, default='9200', help="ElasticSearch Port")

    options, arg = parser.parse_known_args()
    instance = ElasticSearch().host(options.host).port(options.port)
    build_index = BuildIndex(options.docs, options.date, options.index, options.type, TYPE_MAP[options.type], options.delimiter, instance)
    build_index.delete_date_index()
    build_index.rebuild_index()
