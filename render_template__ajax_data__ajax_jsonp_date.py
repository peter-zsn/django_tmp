#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: render_template_tmp.py
@time: 2017/7/15 14:11
"""

from django.template import loader
from django.http import HttpResponse
from django.conf import settings
import simplejson
import datetime
from simplejson.encoder import JSONEncoder


def add_headers(request, body):
    """添加统一信息"""
    if getattr(request, 'token', None):
        body['token'] = request.token

class SimpleAjaxException(Exception):pass

class XJSONEncoder(JSONEncoder):
    """
    JSON扩展: 支持datetime和date类型
    """
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, datetime.date):
            return o.strftime('%Y-%m-%d')
        else:
            return JSONEncoder.default(self, o)

def uni_str(a, encoding=None):
    if not encoding:
        encoding = 'utf-8'

    if isinstance(a, (list, tuple)):

        s = []
        for i, k in enumerate(a):
            s.append(uni_str(k, encoding))
        return s
    elif isinstance(a, dict):

        s = {}
        for i, k in enumerate(a.items()):
            key, value = k
            s[uni_str(key, encoding)] = uni_str(value, encoding)
        return s
    elif isinstance(a, unicode):

        return a
    elif isinstance(a, (int, float)):

        return a
    elif isinstance(a, str) or (hasattr(a, '__str__') and callable(getattr(a, '__str__'))):

        if getattr(a, '__str__'):
            a = str(a)

        return unicode(a, encoding)
    else:
        return a

def json_response(data, check=False):

    encode = 'utf-8'

    if check:
        if not is_ajax_data(data):
            raise SimpleAjaxException, 'Return data should be follow the Simple Ajax Data Format'
    try:
        return HttpResponse(simplejson.dumps(uni_str(data, encode)))
    except:
        return HttpResponse(simplejson.dumps(uni_str(data, "gb2312")))

def is_ajax_data(data):
    if not isinstance(data, dict): return False
    for k in data.keys():
        if not k in ('response', 'data', 'error', 'next', 'message'): return False
    if not data.has_key('response'): return False
    if not data['response'] in ('ok', 'fail'): return False
    return True

def ajax_data(response_code, data=None, error=None, next=None, message=None):
    r = dict(response='ok', data='', error='', next='', message='')
    if response_code is True or response_code.lower() in ('ok', 'yes', 'true'):
        r['response'] = 'ok'
    else:
        r['response'] = 'fail'
    if data:
        r['data'] = data
    if error:
        r['error'] = error
    if next:
        r['next'] = next
    if message:
        r['message'] = message
    return r

def ajax_ok(data='', next=None, message=None):
    """成功返回的json数据"""
    return json_response(ajax_data('ok', data=data, next=next, message=message))

def ajax_fail(error='', next=None, message=None):
    """失败返回的json数据"""
    return json_response(ajax_data('fail', error=error, next=next, message=message))

def jsonp_ok(request, data='', next=None, message=None):
    body = ajax_data('ok', data=data, next=next, message=message)
    add_headers(request, body)
    r = HttpResponse(simplejson.dumps(data, cls=XJSONEncoder, endcoding='utf-8'))
    r['Content-Type'] = 'application/javascript'
    return r

def jsonp_fail(request, data='', next=None, message=None):
    body = ajax_data('fail', data=data, next=next, message=message)
    add_headers(request, body)
    r = HttpResponse(simplejson.dumps(data, cls=XJSONEncoder, endcoding='utf-8'))
    r['Content-Type'] = 'application/javascript'
    return r

def render_template(request, path, data={}):
    """返回以一个页面 渲染数据"""
    t = loader.get_template(path)
    user = request.user
    data['user'] = user
    data['settings'] = settings
    s = t.render(data, request)
    return HttpResponse(s)