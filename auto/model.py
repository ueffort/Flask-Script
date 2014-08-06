# coding=utf-8
from sqlalchemy.orm import backref

__author__ = 'GaoJie'
from auto import app, db, logger

# bind_key 用于绑定到对应的DATABASE
#__bind_key__ = 'users'


class Company(db.Model):
    __tablename__ = 'b_company'
    __autoload__ = True


class Campaign(db.Model):
    __tablename__ = 'b_campaign'
    __autoload__ = True

    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer)
    company = db.relationship(Company, primaryjoin=companyId == Company.id, lazy='dynamic')


class CampaignAdgroup(db.Model):
    __tablename__ = 'b_campaign_adgroup'
    __autoload__ = True

    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer)
    company = db.relationship(Company, primaryjoin=companyId == Company.id, lazy='dynamic')


class CampaignCreative(db.Model):
    __tablename__ = 'b_campaign_creative'
    __autoload__ = True

    id = db.Column(db.Integer, primary_key=True)
    companyId = db.Column(db.Integer)
    company = db.relationship(Company, primaryjoin=companyId == Company.id, lazy='dynamic')

