#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'UbunGit'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

import markdown2

from aiohttp import web

from coroweb import get, post
from apis import Page,APIError, APIValueError, APIResourceNotFoundError,APIPermissionError

from models import next_id, USER, FUNCTION, PERMISSIONS,GOODSCATEGORY
from config import configs

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

PERDEVLEOPER = 1000
PERTESTER = 2000
PERADMINER = 3000
PERYUNYIN = 4000
PERGONGYING = 5000
PERUSER = 6000


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
    s = '%s-%s-%s-%s' % (user.userID, user.passWord, expires, _COOKIE_KEY)
    L = [user.userID, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
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
        s = '%s-%s-%s-%s' % (uid, user.passWord, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

@get('/')
def index():
    '''欢迎页面'''
    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)
    return {
        '__template__': 'index.html',
        "functions":functions
    }

@get('/register')
def register():
    '''注册'''
    return {
        '__template__': 'register.html'
    }

@get('/signin')
def signin():
    '''登录'''
    return {
        '__template__': 'signin.html'
    }



@get('/signout')
def signout(request):
    '''注销'''
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@get('/manage/users')
def manage_users(*, page='1'):
    '''会员管理'''
    permissions = yield from PERMISSIONS.findAll()
    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)

    page_index = get_page_index(page)
    num = yield from USER.findNumber('count(userID)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from USER.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return {
        '__template__': 'manage_users.html',
        'page': p,
        "users":users,
        "functions":functions,
        "permissions":permissions
    }


@get('/api/users')
def api_get_users(*, page='1'):
    '''获取会员列表'''
    page_index = get_page_index(page)
    num = yield from USER.findNumber('count(userID)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())

    users = yield from USER.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)

@get('/api/users/search')
def api_search_users(*, page='1',userName=None, phone=None, email=None ,keyword=None):
    '''搜素会员'''
    where = ""
    arg = []
    isappend = False

    if userName:
        where = where+'username = %s'
        arg.append(userName)
        isappend = True

    if phone:
        if isappend:
            where = where+' and phone = %s'
        else:
            where = where+'phone = %s'
        arg.append(phone)
        isappend = True

    if email:
        if isappend:
            where = where+'and email = %s'
        else:
            where = where+'email = %s'

        arg.append(email)
        isappend = True

    if keyword:
        if isappend:
            where = where+' and (username LIKE %s  or phone LIKE %s  or email LIKE %s )'
            arg.append('%'+keyword+'%')
            arg.append('%'+keyword+'%')
            arg.append('%'+keyword+'%')
        else:
            where = where+'username LIKE %s or phone LIKE %s  or email LIKE %s '
            arg.append('%'+keyword+'%')
            arg.append('%'+keyword+'%')
            arg.append('%'+keyword+'%')


    page_index = get_page_index(page)
    num = yield from USER.findNumber('count(userID)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = yield from USER.findAll(where=where ,orderBy='created_at desc', limit=(p.offset, p.limit),args=arg)
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)




@post('/api/users')
def api_register_user(*, email, name, passwd):
    '''会员注册'''
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = yield from USER.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = USER(userID=uid, userName=name.strip(), email=email, passWord=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), headImage='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    yield from user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/users/update')
def api_update_user( request, *, userID, userName=None, phone=None, email=None, status=None, permissions=None):
    '''修改会员信息'''
    check_admin(request,PERADMINER)
    user = yield from USER.find(userID)
    if not user:
        raise APIError('updateUsers:failed', 'user', 'user not fund.')

    if user.userName != userName.strip() and userName.strip():
        users = yield from USER.findAll('userName=?', [userName])
        if len(users) > 0:
            raise APIError('updateUsers:failed', 'userName', 'userName is already in use.')
        user.userName = userName.strip()

    if user.email != email and _RE_EMAIL.match(email):
        users = yield from USER.findAll('email=?', [email])
        if len(users) > 0:
            raise APIError('updateUsers:failed', 'email', 'Email is already in use.')
        user.email = email

    if user.phone != phone.strip() and phone.strip():
        users = yield from USER.findAll('phone=?', [phone])
        if len(users) > 0:
            raise APIError('updateUsers:failed', 'email', 'Email is already in use.')
        user.phone = phone.strip()

    if  status:
        user.status = status
    if  permissions:
        user.permissions = permissions
    yield from user.update()
    if request.__user__.userID != userID:
        return user
    else:
        # check passwd:
        r = web.Response()
        r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
        user.passwd = '******'
        r.content_type = 'application/json'
        r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
        return r


@post('/api/users/authenticate')
def api_authenticate_user(*, email, passwd):
    '''会员修改密码'''
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = yield from USER.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.userID.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passWord != sha1.hexdigest():
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/manage/function/{id}')
def manage_function(id):
    function = yield from FUNCTION.find(id)
    permissions = yield from PERMISSIONS.findAll()

    functions = yield from FUNCTION.findAll(where='fatherid=?',args=[0])
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=[item.id])
    return {
        '__template__': 'manage_function.html',
        'functions':functions,
        'function':function,
        "permissions":permissions
    }

@get('/api/function')
def api_function(*, permissions):

    num = yield from FUNCTION.findNumber('count(id)',where='permissions>=?',args=permissions)
    if num == 0:
        return dict(functions=())
    function = yield from FUNCTION.findAll('permissions>=?', args=permissions)
    return dict(functions=function)

@get('/api/function/{id}')
def api_get_function(*, id):

    function = yield from FUNCTION.find(id)
    return dict(function=function)


@post('/api/function')
def api_create_function(request, *, name, fatherid, icon, api, permissions):
    check_admin(request,PERADMINER)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not fatherid or not fatherid.strip():
        raise APIValueError('fatherid', 'fatherid cannot be empty.')
    if not icon or not icon.strip():
        raise APIValueError('icon', 'icon cannot be empty.')
    if not api or not api.strip():
        raise APIValueError('api', 'api cannot be empty.')
    if not permissions or not permissions.strip():
        raise APIValueError('permissions', 'permissions cannot be empty.')

    uid = next_id()
    function = FUNCTION(id=uid, name=name.strip(), fatherid=fatherid.strip(), icon=icon.strip(), api=api.strip(), permissions=permissions.strip())
    yield from function.save()
    return function

@post('/api/function/{id}')
def api_update_function(id, request, *, name, fatherid, icon, api, permissions):
    check_admin(request,PERADMINER)
    function = yield from FUNCTION.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not fatherid or not fatherid.strip():
        raise APIValueError('fatherid', 'fatherid cannot be empty.')
    if not icon or not icon.strip():
        raise APIValueError('icon', 'icon cannot be empty.')
    if not api or not api.strip():
        raise APIValueError('api', 'api cannot be empty.')
    if not permissions or not permissions.strip():
        raise APIValueError('permissions', 'permissions cannot be empty.')
    function.name = name.strip()
    function.fatherid = fatherid.strip()
    function.icon = icon.strip()
    function.api = api.strip()
    function.permissions = permissions.strip()

    yield from function.update()
    return function

@post('/api/function/{id}/delete')
def api_delete_function(request, *, id):
    check_admin(request,PERADMINER)
    function = yield from FUNCTION.find(id)
    yield from function.remove()
    return dict(id=id)

@get('/manage/permissions')
def manage_permissions():
    permissions = yield from PERMISSIONS.findAll(orderBy='permissions asc')

    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)
    return {
        '__template__': 'manage_permissions.html',
        'functions':functions,
        "permissions":permissions
    }

@post('/api/permissions')
def api_create_permissions(request, *, name, permissions):
    check_admin(request,PERADMINER)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not permissions or not permissions.strip():
        raise APIValueError('permissions', 'permissions cannot be empty.')

    uid = next_id()
    permissions = PERMISSIONS(id=uid, name=name.strip(), permissions=permissions.strip())
    yield from permissions.save()
    return permissions

@post('/api/permissions/{id}')
def api_update_permissions(id, request, *, name, permissions):
    check_admin(request,PERADMINER)
    permission = yield from PERMISSIONS.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not permissions or not permissions.strip():
        raise APIValueError('permissions', 'permissions cannot be empty.')

    permission.name = name.strip()
    permission.permissions = permissions.strip()
    yield from permission.update()
    return permission


@post('/api/permissions/{id}/delete')
def api_delete_permissions(request, *, id):
    check_admin(request,PERADMINER)
    permissions = yield from PERMISSIONS.find(id)
    yield from permissions.remove()
    return dict(id=id)


@get('/manage/goodsCategory')
def manage_goodsCategory():
    goodsCategorys = yield from GOODSCATEGORY.findAll(where='fatherid=0')
    for item in goodsCategorys:
        item["itemlist"] = yield from GOODSCATEGORY.findAll(where='fatherid=?',args=item.id)
        for sitem in item["itemlist"]:
            sitem["itemlist"] = yield from GOODSCATEGORY.findAll(where='fatherid=?',args=sitem.id)

    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)
    return {
        '__template__': 'manage_goods_category.html',
        'functions':functions,
        "goodsCategorys":goodsCategorys
    }

@post('/api/goodsCategory')
def api_create_goodsCategory(request, *, name, fatherid="0", icon):
    check_admin(request,PERADMINER)


    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not fatherid or not fatherid.strip():
        raise APIValueError('fatherid', 'fatherid cannot be empty.')
    if not icon or not icon.strip():
        raise APIValueError('icon', 'icon cannot be empty.')
    depth = 1;
    if(fatherid != "0"):
        father = yield from GOODSCATEGORY.find(fatherid)
        depth = father.depth+1;
    if(depth>3):
        raise APIValueError('depth', 'depth is too big.')

    uid = next_id()
    goodsCategory = GOODSCATEGORY(id=uid, name=name.strip(), fatherid=fatherid.strip(), icon=icon.strip(), depth=depth)
    yield from goodsCategory.save()
    return goodsCategory

@post('/api/goodsCategory/{id}')
def api_update_goodsCategory(id, request, *, name, fatherid, icon):
    check_admin(request,PERADMINER)
    goodsCategory = yield from GOODSCATEGORY.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not fatherid or not fatherid.strip():
        raise APIValueError('fatherid', 'fatherid cannot be empty.')
    if not icon or not icon.strip():
        raise APIValueError('icon', 'icon cannot be empty.')
    if(fatherid == id):
        raise APIValueError('fatherid', '所属分类不能是自己.')
    depth = 1;
    if(fatherid != "0"):
        father = yield from GOODSCATEGORY.find(fatherid)
        depth = father.depth+1;
    if(depth>3):
        raise APIValueError('depth', 'depth is too big.')



    goodsCategory.name = name.strip()
    goodsCategory.fatherid = fatherid.strip()
    goodsCategory.icon = icon.strip()
    goodsCategory.depth = depth

    yield from goodsCategory.update()
    return goodsCategory

@post('/api/goodsCategory/{id}/delete')
def api_delete_function(request, *, id):
    check_admin(request,PERADMINER)
    goodsCategory = yield from GOODSCATEGORY.find(id)
    yield from goodsCategory.remove()
    return dict(id=id)