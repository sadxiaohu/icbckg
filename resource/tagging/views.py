# -*- coding: utf-8 -*-
import jieba
import json
from django.http import HttpResponse

import icbckg.config as config
import random
from django.views.decorators.csrf import csrf_exempt

print ("Loading tagging docs ......")
docs = open(config.resource_path+"/tagging/docs.txt").read().strip().split("\n")


# 请求获取数据
def get_data(request):
    doc = random.choice(docs)  # 从文档库中随机选一篇
    doc = jieba.cut(doc)  # 分词
    doc = [word for word in doc]
    response = HttpResponse(json.dumps(doc, ensure_ascii=False))
    response["Access-Control-Allow-Origin"] = "*"
    return response


# 提交数据
@csrf_exempt
def submit_data(request):
    if request.method == 'POST':
        result = "not OK"
        data = request.POST.get("data", None)
        if data is not None:
            data = json.loads(data)
            if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                ip = request.META['HTTP_X_FORWARDED_FOR']
            else:
                ip = request.META['REMOTE_ADDR']
            data["ip"] = ip
            write_result(json.dumps(data,ensure_ascii=False))
            result = "OK"
        response = HttpResponse(result)
        response["Access-Control-Allow-Origin"] = "*"
        return response


def write_result(s):
    results_file = open(config.resource_path + "/tagging/results", "a")
    results_file.write(s + "\n")
    results_file.close()


