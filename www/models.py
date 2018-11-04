#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Models for user, blog, comment.
'''

__author__ = 'Michael Liao'

import time, uuid
import random
import string

from orm import Model, StringField, BooleanField, FloatField, TextField,IntegerField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

def next_text(len):
    return ''.join(random.sample(string.ascii_letters + string.digits, len))

'''用户'''
class USER(Model):
    __table__ = 'USERS'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    userName = StringField(ddl='varchar(25)')
    passwd = StringField(ddl='varchar(50)')
    phone = StringField(ddl='varchar(11)')
    status = IntegerField()
    permissions = IntegerField()
    headImage = StringField(ddl='varchar(500)')
    recommendid = StringField(ddl='varchar(50)')
    recommendCode = StringField(ddl='varchar(6)')
    depth = IntegerField()
    created_at = FloatField(default=time.time() * 1000)


'''功能'''
class FUNCTION(Model):
    __table__ = 'FUNCTION'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(25)')
    fatherid = StringField(ddl='varchar(50)')
    icon = StringField(ddl='varchar(20)')
    api = StringField(ddl='varchar(50)')
    permissions = IntegerField()

'''权限'''
class PERMISSIONS(Model):

    __table__ = 'PERMISSIONS'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(25)')
    permissions = IntegerField()

'''app功能配置列表'''
class APPFUNVCTION(Model):

    __table__ = 'APPFUNVCTION'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(25)')

'''app路由列表'''
class APPWAY(Model):
    __table__ = 'APPWAY'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(25)')
    appfuncid = StringField(ddl='varchar(50)')
    url = StringField(ddl='varchar(125)')
    icon = StringField(ddl='varchar(500)')
    soft = IntegerField()






