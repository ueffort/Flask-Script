# coding=utf-8
import sys
from common.decorators import responsed
from flask import request
from auto import app
from auto.task import task_blueprint

__author__ = 'GaoJie'


@app.route('/test', methods=['post', 'get'])
@responsed
def test():
	if request.method == 'post':
		print 'Post:', request.form
	elif request.method == 'get':
		print 'Get:', request.args


@app.errorhandler(404)
@responsed
def task_404(e):
	path_list = request.path[1:].split('/')
	if path_list[0] in task_blueprint.keys():
		print 'Task: %s ' % path_list[0]
		task_module = sys.modules['%s.task.%s' % (__package__, path_list[0])]
		# 需在每个task模块中添加action_list，用于判断可以执行的
		task_action = getattr(task_module, 'action_list')
		print 'Action List: %s ' % [value for value in task_action]
	else:
		print 'Task List: %s' % ' , '.join(task_blueprint.keys())
		print 'You need chose one'

#app.add_url_rule('/index', view_func=index)

# 将所有任务蓝图注册
for item in task_blueprint.values():
	app.register_blueprint(item)
