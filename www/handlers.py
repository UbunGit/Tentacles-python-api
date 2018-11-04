#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'UbunGit'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page,APIError, APIValueError, APIResourceNotFoundError,APIPermissionError

from models import next_id,next_text, USER, FUNCTION,PERMISSIONS,APPFUNVCTION,APPWAY
from config import configs

COOKIE_NAME = 'awesession'

_COOKIE_KEY = configs.session.secret


PERDEVLEOPER = 1000 #开发者
PERTESTER = 2000 #测试者
PERADMINER = 3000 #管理员
PERYUNYIN = 4000 #运营者
PERGONGYING = 5000 #供应商
PERUSER = 6000 #用户


def check_admin(request,permissions):

    if request.__user__ is None:
        raise APIPermissionError()

    if request.__user__.permissions > permissions:
        raise APIPermissionError()



def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from USER.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None















