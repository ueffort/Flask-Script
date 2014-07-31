Flask-Script
============

基于Flask的命令行框架

#首先安装
pip install virtualenv

#在脚本目录中执行
virtualenv --system-site-packages env

#Linux下通过下面命令安装类库
./env/bin/pip install xxx

#Windows下通过下面命令安装类库
./env/Scripts/pip  install xxx

#也可以通过命令将当前环境切换为env，路径也是需要区分linux还是windows
#进入
source ./env/bin/active
#windows env\Scripts\activate
#退出
deactivate

#脚本中默认添加的是linux的执行命令
#!evn/bin/python

#环境所需安装类库
flask
flask-mail
flask-sqlalchemy
redis

#settings为通用配置，和执行环境无关的配置设置
#复制production_settings_template.py为production_settings.py，并修改对应的配置信息
#需要保证local_settings.py和production_settings_template.py的配置项一致
#以APP_name为开头的%s_CONFIG为应用的单独配置，可以用于划分数据库等，如果在settings中已经存在，则需要手动进行合并


#调用脚本方式
script uri --method=get --xx=xx
#method为框架所需，配合http协议区分脚本的执行方式，默认为get
#--开头的作为参数传入

#auto应用，包含基本的自动化脚本，内部通过task来划分脚本
#uri参数的组织方式为：auto/<task>/<action>
#划分信息可以查看auto/route.py

#test应用，包含对其他应用的单元测试