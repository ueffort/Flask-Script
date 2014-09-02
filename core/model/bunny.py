# coding=utf-8
import json
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

__author__ = 'GaoJie'
from flask import current_app

# bind_key 用于绑定到对应的DATABASE
#__bind_key__ = 'users'
db = SQLAlchemy()
bunny_engine = db.get_engine(current_app, 'bunny')

class Company(db.Model):
    __tablename__ = 'b_company'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    id = db.Column(db.Integer, primary_key=True)


class Campaign(db.Model):
    __tablename__ = 'b_campaign'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer, db.ForeignKey(Company.id))
    company = db.relationship(Company, primaryjoin=companyId == Company.id, lazy='joined')


class CampaignAdgroup(db.Model):
    __tablename__ = 'b_campaign_adgroup'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer, db.ForeignKey(Company.id))
    company = db.relationship(Company, primaryjoin=companyId == Company.id, lazy='joined')


class CampaignCreative(db.Model):
    __tablename__ = 'b_campaign_creative'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer, db.ForeignKey(Company.id))
    company = db.relationship(Company, primaryjoin=companyId == Company.id, lazy='joined')
    campaignId = db.Column(db.Integer, db.ForeignKey(Campaign.id))
    campaign = db.relationship(Campaign, primaryjoin=campaignId == Campaign.id, lazy='joined')
    #adx = db.relationship(CreativeAdx, lazy='joined')

    def get_format_template(self):
        return json.loads(self.adFormatTemplate)

    def set_format_template(self, object):
        self.adFormatTemplate = json.dumps(object)


class CreativeAdx(db.Model):
    __tablename__ = 'b_creative_adx'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    creativeId = db.Column(db.Integer, db.ForeignKey(CampaignCreative.id))
    adxId = db.Column(db.Integer)
    creative = db.relationship(CampaignCreative, primaryjoin=creativeId == CampaignCreative.id, lazy='joined')
