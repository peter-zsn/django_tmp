#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: get_post_boby.py
@time: 2017/7/15 14:41
"""

import json
import time
import datetime
import re

from django.http.request import QueryDict

def type_default_value(type):
    "返回基本类型默认值, 没有识别的类型返回None"
    tab = {str:"", unicode:u"", list:[], int:0}
    return tab.get(type)

def casts(self, **kw):
    """批量转换url参数类型post, get, json等"""
    args = {}
    for k, typ in kw.iteritems():
        v = self.get(k)
        if isinstance(typ, basestring):
            if typ == 'json':
                try:
                    v = json.loads(v) if v else {}
                except:
                    pass
            elif typ == 'datetime':
                if v:
                    t = time.strptime(v, "%Y-%m-%d %H:%M:%S")
                    v = datetime.datetime(*t[:6])
                else:
                    v = None
            else:
                m = re.match(typ, v or '')
                groups = m.groups() if m else ()
                groups = [g for g in groups if g is not None]
                v = groups[0] if groups else ''
        else:
            defv = type_default_value(typ)
            try:
                v = typ(v) if v is not None else defv
            except:
                v = defv
        args[k] = v
    return args

def loads(self):
    """解析json参数"""
    try:
        o = json.loads(self.body)
    except:
        o = {}
    return o

QueryDict.casts = casts
QueryDict.loads = loads()
