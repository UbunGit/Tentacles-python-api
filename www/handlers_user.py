#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'UbunGit'

' url handlers '


from handlers import *
import markdown2

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_PHONE = re.compile(r'^1\d{10}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@get('/')
def index():
    '''
    ## 欢迎页面
    '''
    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)
    return {
        '__template__': 'index.html',
        "functions":functions
    }
@get('/test')
def test():
    '''
    ## 测试
    '''

    return {
        '__template__': 'test.html'
    }

@get('/apidoc')
def apidoc():
    '''
    ## api文档
    '''
    with open('./doc/api.md', 'r') as f:
        text = f.read()
        return {
            '__template__': markdown2.markdown(text)
        }

@get('/register')
def register():
    '''
    ## 注册
    '''
    return {
        '__template__': 'register.html'
    }

@get('/signin')
def signin():
    '''
    ## 登录
    '''
    return {
        '__template__': 'signin.html'
    }

@get('/manage/function/{id}')
def manage_function(id):
    '''
    ## 功能管理
    :param id: 功能id false   string
    :return: {
        '__template__': 'manage_function.html', //模版
        'functions':functions,  //功能列表
        'function':function,    //功能信息
        "permissions":permissions   //权限列表
    }
    '''
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


@post('/api/user/logout')
def signout(request):
    '''
    ## 注销
    '''
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    r.content_type = 'application/json'
    a =  {
        "status":"0"
    }
    r.body = json.dumps(a, ensure_ascii=False).encode('utf-8')
    return r


@get('/manage/users')
def manage_users(*, page='1'):
    '''
    ## 会员管理
    '''
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

@post('/api/register')
def api_add_user(*, phone,  passwd, recommendCode=None, permissions=0):
    '''
    用户注册
    :param phone: 手机号码 notnull
    :param passwd: 密码 notnull 经过 ":passwd"sha1加密
    :param recommendCode: 推荐码 defual None
    :param permissions: 权限 defual 0
    :return:
    '''
    if not phone or not _RE_PHONE.match(phone):
        raise APIValueError('register:failed', '手机号码错误.')
    if not passwd:
        raise APIValueError('register:failed', '密码输入错误.')
    reuser = None
    if recommendCode:
        users = yield from USER.findAll('recommendCode=?', [recommendCode])
        if len(users) == 0:
            raise APIValueError('register:failed', '推荐码输入有误.')
        else:
            reuser = users[0]
            if reuser.depth+1>3:
                raise APIValueError('register:failed', '推荐人不能推荐别人.')

    reuserid = ''
    reDepth = 1;
    if reuser:
        reuserid = reuser.id;
        reDepth = reuser.depth+1;

    users = yield from USER.findAll('phone=?', [phone])
    if len(users) > 0:
        raise APIError('register:failed', 'phone', '手机号码已存在.')


    '''创建用户邀请码'''
    reCode = next_text(6);
    users = yield from USER.findAll('recommendCode=?', [reCode])
    if len(users) > 0:
        raise APIValueError('register:failed', '系统错误，请稍后再试.')


    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = USER(id=uid,
                userName = reCode,
                passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                phone = phone,
                status = 0,
                permissions = permissions,
                recommendid = reuserid,
                recommendCode = reCode,
                depth = reDepth,
                headImage='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(reCode.encode('utf-8')).hexdigest()
                )
    yield from user.save()
    return dict()

@post('/api/user/delete')
def api_delete_user(*, phone):
    '''
    删除会员
    :param phone: 手机号码 notnull
    :return:
    '''
    if not phone or not _RE_PHONE.match(phone):
        raise APIValueError('register:failed', '手机号码错误.')
    users = yield from USER.findAll('phone=?', [phone])
    if len(users) == 0:
        raise APIError('register:failed', 'phone', '手机号码不存在.')
    user = users[0]
    yield from user.remove()
    return dict()

@post('/api/user/update')
def api_update_user(request, *, phone=None, userName=None, passwd=None, headImage=None):
    '''
    会员修改用户信息
    :param request:
    :param phone: 手机号码 defual None
    :param userName: 用户名 defual None
    :param passwd: 密码 defual None
    :param headImage: 头像  defual None
    :return:
    '''

    isout = False
    user = request.__user__

    if not user:
        raise APIError('updateuser:failed', 'user', '用户未登录.')


    if phone:
        if  not _RE_PHONE.match(phone):
            raise APIValueError('updateuser:failed', '手机号码错误.')
        else:
            users = yield from USER.findAll('phone=?', [phone])
            if len(users) > 0:
                raise APIError('updateuser:failed', 'phone', '手机号码已存在.')
            else:
                user.phone = phone
                isout = True


    if  passwd:
        sha1_passwd = '%s:%s' % (user.id, passwd)
        user.passwd = hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest()
        iisout = True

    if userName:
        if not userName or not userName.strip():
            raise APIError('updateuser:failed', 'userName', '用户名错误.')
        else:
            user.userName = userName

    if headImage:
        user.permissions = headImage

    yield from user.update();
    if(isout):
        r = web.Response()
        r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
        user.passwd = '******'
        r.content_type = 'application/json'
        r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
        return r
    else:
        return dict()

@post('/api/users/login')
def api_login(*, phone, passwd, verCode=None):
    '''
    用户登录
    :param phone: 手机号码
    :param passwd: 密码
    :param verCode: 验证码
    :return:
    '''

    if not phone:
        raise APIError('login:failed', 'phone', '手机号码不能为空.')
    if not passwd:
        raise APIValueError('login:failed', '密码错误.')
    users = yield from USER.findAll('phone=?', [phone])
    if len(users) == 0:
        raise APIValueError('login:failed', '用户不存在.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd', '用户名或密码输入有误.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passWord = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r





@get('/api/users/search')
def api_search_users(*, page='1', phone=None, keyword=None):
    '''
    ## 搜素会员
    '''
    where = ""
    arg = []
    isappend = False


    if phone:
        if isappend:
            where = where+' and phone = %s'
        else:
            where = where+'phone = %s'
        arg.append(phone)
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




@post('/api/function')
def api_add_function(request, *, name, fatherid, icon, api, permissions):
    '''
    ## 创建功能
    :param request:
    :param name: 功能名
    :param fatherid: 功能父id
    :param icon: icon
    :param api: api
    :param permissions: 权限
    :return: {
    function
    }
    '''
    check_admin(request,PERADMINER)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not fatherid or not fatherid.strip():
        raise APIValueError('fatherid', 'fatherid cannot be empty.')
    if not icon or not icon.strip():
        raise APIValueError('icon', 'icon cannot be empty.')
    if not api or not api.strip():
        raise APIValueError('api', 'api cannot be empty.')

    uid = next_id()
    function = FUNCTION(id=uid, name=name.strip(), fatherid=fatherid.strip(), icon=icon.strip(), api=api.strip(), permissions=permissions)
    yield from function.save()
    return function

@post('/api/function/delete/{id}')
def api_delete_function(id,request):
    '''
    删除功能
    :param id: 功能id
    :param request:
    :return: {
    id 被删除的id
    }
    '''
    check_admin(request,PERADMINER)
    function = yield from FUNCTION.find(id)
    yield from function.remove()
    return dict(id=id)

@post('/api/function/update/{id}')
def api_update_function(id, request, *, name, fatherid, icon, api, permissions):
    '''
    ## 更新功能内容
    :param id: 功能id
    :param request:
    :param name: 功能名
    :param fatherid: 功能父id
    :param icon:
    :param api:
    :param permissions:
    :return: {
        function
    }
    '''
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

    function.name = name.strip()
    function.fatherid = fatherid.strip()
    function.icon = icon.strip()
    function.api = api.strip()
    function.permissions = permissions

    yield from function.update()
    return function

@post('/api/functions')
def api_functions(*, permissions):
    '''
    ## 功能列表
    :param permissions: 权限
    :return:
    '''
    num = yield from FUNCTION.findNumber('count(id)',where='permissions>=?',args=permissions)
    if num == 0:
        return dict(functions=())
    functions = yield from FUNCTION.findAll(where='fatherid=?',args=[0])
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=[item.id])
    return dict(functions=functions)

@get('/manage/appway')
def register():
    '''
    ## app功能配置
    '''

    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)
    return {
        '__template__': 'appway.html',
        "functions":functions
    }

@post('/api/appfunction')
def api_addAppfunction(*,name):
    '''
    添加app所需配置的功能
    :param name: 功能名称
    :return:
    '''
    if not name or not name.strip():
        raise APIValueError('name', '功能名不能为空.')
    funs = yield from APPFUNVCTION.findAll(where='name=?',args=[name])
    if len(funs) > 0:
        raise APIValueError('name', '功能名不能重复.')
    uid = next_id()
    appfun = APPFUNVCTION(id=uid,name=name.strip())
    yield from appfun.save()
    return dict()

@post('/api/appfunction/delete/{id}')
def api_delete_appfunction(id,request):
    '''
    删除app所需配置的功能
    :param id:
    :param request:
    :return:
    '''
    check_admin(request,PERADMINER)
    appfunc = yield from APPFUNVCTION.find(id)
    yield from appfunc.remove()
    return dict(id=id)

@post('/api/appfunction/update/{id}')
def api_update_appfunction(id,request,*,name):
    '''
    修改app所需配置的功能名
    :param id:
    :param request:
    :return:
    '''
    check_admin(request,PERADMINER)
    if not name or not name.strip():
        raise APIValueError('name', '功能名不能为空.')
    funs = yield from APPFUNVCTION.findAll(where='name=?',args=[name])
    if len(funs) > 0:
        raise APIValueError('name', '未找到需要修改的功能.')
    appfunc = yield from APPFUNVCTION.find(id)
    appfunc.name = name
    yield from appfunc.update()
    return appfunc

@post('/api/appfunctions')
def api_appfunctions():
    '''
    查询所有所需配置的功能名
    :return:
    '''

    appfunctions = yield from APPFUNVCTION.findAll()
    return dict(appfunctions=appfunctions)

@post('/api/appway')
def api_addappway(*,name,appfuncid,url,icon,soft):
    '''
    添加app跳转功能
    :param name: 跳转名
    :param appfuncid: 所属功能id
    :param url: url
    :param icon: 功能图片
    :param soft: 排序
    :return:
    '''
    if not name or not name.strip():
        raise APIValueError('name', '跳转功能名不能为空.')
    if not appfuncid or not appfuncid.strip():
        raise APIValueError('name', '跳转所属类型不能为空.')
    if not url or not url.strip():
        raise APIValueError('name', '跳转url不能为空.')
    if not icon or not icon.strip():
        icon=""
    if not soft:
        soft=0
    appway = APPWAY(name=name.strip(),
                    appfuncid=appfuncid.strip(),
                    url = url.strip(),
                    icon = icon,
                    soft = soft
                    )
    yield from appway.save()
    return dict()

@post('/api/appway/delete')
def api_delete_appway(request,*,id):
    '''
    删除app跳转功能
    :param id:
    :return:
    '''
    check_admin(request,PERADMINER)
    appway = yield from APPWAY.find(id)
    yield from appway.remove()
    return dict(id=id)

@post('/api/appway/update')
def api_update_appway(*,id,name=None ,appfuncid=None ,url=None ,icon=None, soft=None):
    '''
    添加app跳转功能
    :param name: 跳转名
    :param appfuncid: 所属功能id
    :param url: url
    :param icon: 功能图片
    :param soft: 排序
    :return:
    '''
    appways = yield from APPWAY.findAll(where="id=?",args=id)
    if len(appways=0):
        raise APIValueError('name', '未找到对应跳转功能.')
    appway = appways[0]
    if name:
        if not name.strip():
            raise APIValueError('name', '跳转功能名不能为空.')
        else:
            appway.name = name

    if appfuncid:
        if not appfuncid.strip():
            raise APIValueError('name', '跳转功能名不能为空.')
        else:
            appway.appfuncid = appfuncid


    if url:
        if not url.strip():
            raise APIValueError('name', '跳转功能名不能为空.')
        else:
            appway.url = url

    if icon:
        if not icon.strip():
            appway.icon = ""
        else:
            appway.icon = icon

    if soft:
        appway.soft = soft
    yield from appway.update()
    return dict()

@post('/api/appways')
def api_appways(*,appfuncid):
    '''
    查询app配置功能下的跳转功能列表
    :param appfuncid: 配置功能id
    :return:
    '''

    appways = yield from APPWAY.findAll(where="appfuncid=?",args=appfuncid,orderBy="soft")
    return dict(appways=appways)















