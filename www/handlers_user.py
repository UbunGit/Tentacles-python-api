#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'UbunGit'

' url handlers '

from handlers import *

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
def api_delete_function(id,request):
    check_admin(request,PERADMINER)
    function = yield from FUNCTION.find(id)
    yield from function.remove()
    return dict(id=id)



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


