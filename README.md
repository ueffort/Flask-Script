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
`script.py uri --xx=xx`

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
* 一个应用建立一个test单元，在`__init__`中添加应用context，让测试进入app的环境

> `python script.py auto_test discover arg `

* arg: -s(start dir) -p(pattern file)
* 测试文件都由test开头，最小测试单位为一个测试文件，如果要单独执行更细粒度的测试，则需要自己写对应的测试脚本__main__

## 各目录说明
1.flask_script目录
> 框架相关的文件

2.core目录：
> 内部应用的核心，数据库或者第三方系统的访问库

3.ext目录：
> 共用逻辑处理文件
> 响应框架通知的处理文件
> 与应用无关的工具库

## 开发计划
1. 整合官方的Flask-script的功能：参数提示
2. 抽象出manager和command对象，简化开发代码
