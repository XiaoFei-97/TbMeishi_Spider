#!/usr/bin/env python
# coding=utf-8

# 本地的数据库
MONGO_URL = 'localhost'

# 数据库的名称
MONGO_DB = 'taobao'

# 数据库的表名
MONGO_TABLE = 'products'

# 关闭load-images的功能，加快运行速度，默认开启，开启disk-cache缓存，默认关闭
SERVICE_ARGS = ['--load-images=false', '--disk-cache=true']


KEYWORD = '美食'
