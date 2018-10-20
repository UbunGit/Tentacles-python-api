#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'UbunGit'

' url handlers '

from handlers import *


'''
商品分类
'''
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

'''
商品管理
'''
@get('/manage/goods')
def manage_goods( *, page='1',id='0'):

    functions = yield from FUNCTION.findAll(where='fatherid=0')
    for item in functions:
        item["itemlist"] = yield from FUNCTION.findAll(where='fatherid=?',args=item.id)


    goodsCategorys = yield from GOODSCATEGORY.findAll(where='fatherid=0')
    for item in goodsCategorys:
        item["itemlist"] = yield from GOODSCATEGORY.findAll(where='fatherid=?',args=item.id)
        for sitem in item["itemlist"]:
            sitem["itemlist"] = yield from GOODSCATEGORY.findAll(where='fatherid=?',args=sitem.id)
    return {
        '__template__': 'manage_goods.html',
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
def api_delete_goodsCategory(request, *, id):
    check_admin(request,PERADMINER)
    goodsCategory = yield from GOODSCATEGORY.find(id)
    yield from goodsCategory.remove()
    return dict(id=id)


@post('/api/attribute')
def api_add_attribute(request, *, name):
    check_admin(request,PERADMINER)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')

    attributes = yield from ATTRIBUTENAME.findNumber('count(id)',where='name=?',args=[name])
    if attributes>0:
        raise APIError('add_attribute:failed', 'attribute', 'attribute is already in use.')

    uid = next_id()
    attribute = ATTRIBUTENAME(id=uid, name=name.strip())
    yield from attribute.save()
    return attribute

'''删除属性'''
@post('/api/attribute/{id}/delete')
def api_delete_attribute(request, *, id):
    check_admin(request,PERADMINER)
    attribute = yield from ATTRIBUTENAME.find(id)
    yield from attribute.remove()
    return dict()


'''
查询类别下已关联与未关联商品属性
'''
@get('/api/attributes')
def api_attributes(request, *, categoryid):

    '''查询分类下所有已关联的属性id列表'''
    hasCategoryAtts = yield from CATEGORY_ATTRIBUTENAME.findAll(where='categoryid=?',args=categoryid);
    attributeids = [];
    atts = None;
    notAtts = None;

    for item in hasCategoryAtts:
        attributeids.append(item.attributeid);

    if len(attributeids)>0:
        atts = yield from ATTRIBUTENAME.findAll(where='id in ?',args=[attributeids])
        notAtts = yield from ATTRIBUTENAME.findAll(where='id not in ?',args=[attributeids])
    else:
        notAtts = yield from ATTRIBUTENAME.findAll()

    return dict(atts=atts,notAtts=notAtts)
'''
分类关联属性
'''
@post('/api/linkAttributes')
def api_linkAttributes(request, *, categoryid, attributeid):
    check_admin(request,PERADMINER)
    hasCategoryAtts = yield from CATEGORY_ATTRIBUTENAME.findAll(where='categoryid=? and attributeid=?',args=[categoryid,attributeid]);
    if hasCategoryAtts:
        raise APIError('attributeid:failed', 'attributeid', 'attributeid is already in link.')

    uid = next_id()
    attribute_att = CATEGORY_ATTRIBUTENAME(id=uid, categoryid=categoryid,attributeid=attributeid);
    yield from attribute_att.save()
    return dict()

'''
分类取消关联属性
'''
@post('/api/revokeAttributes')
def api_revokeAttributes(request, *, categoryid, attributeid):
    check_admin(request,PERADMINER)
    categoryAtts = yield from CATEGORY_ATTRIBUTENAME.findAll(where='categoryid=? and attributeid=?',args=[categoryid,attributeid]);
    if not categoryAtts:
        raise APIError('attributeid:failed', 'attributeid', 'attributeid not find.')
    for item in categoryAtts:
        yield from item.remove()

    return dict()



@post('/api/goodsspu')
def api_create_goodsspu(request, *, name, content="", dm_img="/static/img/pro.jpg", dm_price, keywords="",categoryid):

    check_admin(request,PERGONGYING)

    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not categoryid:
        raise APIValueError('categoryid', 'categoryid cannot be empty.')
    mallid = request.__user__.userID
    uid = next_id()
    goodsspu = GOODS_SPU(id=uid, name=name.strip(),
                         content=content.strip(), dm_img=dm_img.strip(),
                         dm_price=dm_price.strip(),keywords = keywords.strip(),
                         categoryid=categoryid,mallid=mallid
                         )
    yield from goodsspu.save()
    return dict()

@post('/api/goodsspu/{id}')
def api_update_goodsspu(id, request, *, name, content="", dm_img="/static/img/pro.jpg", dm_price, keywords="",categoryid):

    check_admin(request,PERGONGYING)
    goodsspu = yield from GOODS_SPU.find(id)
    if not name or not name.strip():
        raise APIValueError('name', 'name cannot be empty.')
    if not categoryid:
        raise APIValueError('categoryid', 'categoryid cannot be empty.')
    mallid = request.__user__.userID
    goodsspu.name = name.strip();
    goodsspu.content = content.strip();
    goodsspu.dm_img = dm_img.strip();
    goodsspu.dm_price = dm_price.strip();
    goodsspu.keywords = keywords.strip();
    goodsspu.categoryid = categoryid.strip();
    goodsspu.mallid = mallid;
    yield from goodsspu.update()
    return dict()

@post('/api/goodsspus')
def api_goodsspus(request, *, keywords=None,page="1"):

    mallid = request.__user__.userID
    '''搜素会员'''
    where = ""
    arg = []
    isappend = False
    if request.__user__.permissions > PERADMINER:
        where = where+'mallid = %s'
        arg.append(mallid)
        isappend = True

    if keywords:
        if isappend:
            where = where+' and (name LIKE %s  or content LIKE %s  or keywords LIKE %s )'
            arg.append('%'+keywords+'%')
            arg.append('%'+keywords+'%')
            arg.append('%'+keywords+'%')
        else:
            where = where+'name LIKE %s or content LIKE %s  or keywords LIKE %s '
            arg.append('%'+keywords+'%')
            arg.append('%'+keywords+'%')
            arg.append('%'+keywords+'%')


    page_index = get_page_index(page)
    num = 0
    if where.strip():
        num = yield from GOODS_SPU.findNumber('count(id)',where=where ,args=arg)
    else:
        num = yield from GOODS_SPU.findNumber('count(id)')

    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    if where.strip():
        goodsspus = yield from GOODS_SPU.findAll(where=where ,orderBy='id desc', limit=(p.offset, p.limit),args=arg)
    else:
        goodsspus = yield from GOODS_SPU.findAll(orderBy='id desc', limit=(p.offset, p.limit))
    return dict(page=p, goodsspus=goodsspus)

