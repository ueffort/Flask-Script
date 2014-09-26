# coding=utf-8
from core.model.bunny import db, bunny_engine
from flask.ext.sqlalchemy import SQLAlchemy

__author__ = 'GaoJie'


class Cert(db.Model):
    __tablename__ = 'b_org_cert'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    id = db.Column(db.Integer, primary_key=True)


class CertAudit(db.Model):
    __tablename__ = 'b_org_cert_audit'
    __table_args__ = {'autoload': True, 'autoload_with': bunny_engine}

    certId = db.Column(db.Integer, db.ForeignKey(Cert.id))
    adxId = db.Column(db.Integer)
    creative = db.relationship(Cert, primaryjoin=certId == Cert.id)