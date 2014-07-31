from flask import Config

__author__ = 'GaoJie'


class FlaskConfig(Config):
	last_obj = None

	def from_object(self, obj):
		self.last_obj = obj
		super(FlaskConfig, self).from_object(obj)
		return obj