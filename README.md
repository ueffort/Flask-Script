Flask-Script
============

基于Flask的命令行框架

#环境准备
1.安装python的virtualenv
>>`pip install virtualenv`

2.在源码目录中执行
>>`virtualenv --system-site-packages --python=python2.7 env`

3.安装所需类库
### 安装脚本 ###
* Linux下：`./install.sh`
* Windows下：`./install.bat` 

### 手动安装：###
* Linux下：`./env/bin/pip install xxx`
* Windows下：`./env/Scripts/pip install xxx`

4.环境所需安装类库
* flask
* flask-mail
* flask-sqlalchemy
* redis

#注意
1.脚本中默认添加的是linux的执行命令
`#!evn/bin/python`

#配置
* `settings`为通用配置，和执行环境无关的配置设置
* 复制`production_settings_template.py`为`production_settings.py`，并修改对应的配置信息 
* 需要保证`local_settings.py`和`production_settings_template.py`的配置项一致
* 以`APP_name`为开头的`%s_CONFIG`为应用的单独配置，可以用于划分数据库等，如果在`settings`中已经存在，则需要手动进行合并

#执行
1.在命令行执行：
`script uri --method=get --xx=xx`

>> 其中`method`为框架所需，配合http协议区分脚本的执行方式，默认为`get`

>> --开头的作为参数传入

#内部说明
## auto应用
> 包含基本的自动化脚本，内部通过`task`来划分脚本

* `uri`参数的组织方式为：`auto/\<task\>/\<action\>`
* 划分信息可以查看`auto/route.py `

## test应用
> 包含对其他应用的单元测试

* 整合基本的`unittest`，`uri`参数为`settings`中设置的`TEST_MODULE`即可进入单元测试
* 后续参数与`unittest`参数一致即可，如执行所有test: `discover`
* 每个测试脚本只能访问一个app环境，加载对应的环境module
