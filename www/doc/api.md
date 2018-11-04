#Ubungit-python-api
[toc]

## /api/appfunction
    添加app所需配置的功能
    :param name: 功能名称
    :return:
    
## /api/function
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
    
## /api/register
    用户注册
    :param phone: 手机号码 notnull
    :param passwd: 密码 notnull 经过 ":passwd"sha1加密
    :param recommendCode: 推荐码 defual None
    :param permissions: 权限 defual 0
    :return:
    
## /api/appway
    添加app跳转功能
    :param name: 跳转名
    :param appfuncid: 所属功能id
    :param url: url
    :param icon: 功能图片
    :param soft: 排序
    :return:
    
## /api/appfunctions
    查询所有所需配置的功能名
    :return:
    
## /api/appways
    查询app配置功能下的跳转功能列表
    :param appfuncid: 配置功能id
    :return:
    
## /api/appfunction/delete/{id}
    删除app所需配置的功能
    :param id:
    :param request:
    :return:
    
## /api/appway/delete
    删除app跳转功能
    :param id:
    :return:
    
## /api/function/delete/{id}
    删除功能
    :param id: 功能id
    :param request:
    :return: {
    id 被删除的id
    }
    
## /api/user/delete
    删除会员
    :param phone: 手机号码 notnull
    :return:
    
## /api/functions
    ## 功能列表
    :param permissions: 权限
    :return:
    
## /api/users/login
    用户登录
    :param phone: 手机号码
    :param passwd: 密码
    :param verCode: 验证码
    :return:
    
## /api/users/search
    ## 搜素会员
    
## /api/appfunction/update/{id}
    修改app所需配置的功能名
    :param id:
    :param request:
    :return:
    
## /api/appway/update
    添加app跳转功能
    :param name: 跳转名
    :param appfuncid: 所属功能id
    :param url: url
    :param icon: 功能图片
    :param soft: 排序
    :return:
    
## /api/function/update/{id}
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
    
## /api/user/update
    会员修改用户信息
    :param request:
    :param phone: 手机号码 defual None
    :param userName: 用户名 defual None
    :param passwd: 密码 defual None
    :param headImage: 头像  defual None
    :return:
    
## /api/user/logout
    ## 注销
    