#coding=utf-8

"""
@varsion: ??
@author: 张帅男
@file: middleware.py
@time: 2017/7/15 14:46
"""

import traceback
import simplejson as json
from django.http import HttpResponse, Http404
from django.conf import settings

class AuthenticationMiddleware(object):
    def process_request(self, request):
        try:
            return self._process_request(request)
        except:
            exc = traceback.format_exc()
            if settings.DEBUG:
                print exc

    def cross_domain(self, request, response=None):
        """
        添加跨域头
        """
        origin = request.META.get('HTTP_ORIGIN', '*')
        if request.method == 'OPTIONS' and not response:
            response = HttpResponse()
        if not response:
            return
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Methods'] = 'GET,POST'
        response['Access-Control-Allow-Headers'] = 'x-requested-with,content-type,App-Type'
        response['Access-Control-Max-Age'] = '1728000'
        return response

    def _process_request(self, request):
        # REQUEST过期, 使用QUERY代替
        query = request.GET.copy()
        query.update(request.POST)
        # 把body参数合并到QUERY
        try:
            body = json.loads(request.body)
            query.update(body)
        except:
            pass
        request.QUERY = query

        r = self.cross_domain(request)
        if r:
            return r

    def process_response(self, request, response):
        # 更新token
        if getattr(request, '_newtoken', None):
            #更新token
            pass
        # 添加跨域头
        self.cross_domain(request, response)

        return response

    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            return

        path = str(request.path)
        rootdir = path.split('/', 2)[1]
        if isinstance(exception, Http404):
            return
        if isinstance(exception, AssertionError):
            message = exception.message
            if not message:
                return
            if isinstance(message, Http404):
                raise message
            raise Http404('AssertionError: %s' % exception.message)

        # 如果请求的路径为 js css 文件 不处理
        if rootdir in ('stastic',):
            return
        exc = traceback.format_exc()
        if settings.DEBUG:
            print exc
        if request.is_ajax():
            return HttpResponse("error", status=500)
        if request.method == "POST":
            return HttpResponse("error", status=500)
        return HttpResponse("系统错误,请联系客服!", status=500)