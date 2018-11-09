# -*- coding: utf-8 -*-
import serviceKG
import serviceQA
import json
from django.http import HttpResponse
import owlNeo4j


# 与图谱相关
def graph(request):
    question = request.GET.get('q', None)#request.GET返回URL，get（'q',None）表示取URL中q的内容，如果没有q，则取Nnoe,如http://10.1.1.28:8000/api/graph/qa/?q=北航的现任校长是哪个学校毕业的
    neoid = request.GET.get('id', None)
    # signal = request.GET.get('signal', None)
    # owlNeo4j.set_KB(signal)
    neoid = int(neoid) if neoid is not None else None
    autopick = request.GET.get('autopick', "false").lower()
    if autopick == "true":
        autopick = True
    else:
        autopick = False
    response = HttpResponse(json.dumps(serviceKG.knowledge_graph(question, neoid=neoid, autopick=autopick), ensure_ascii=False))
    response["Access-Control-Allow-Origin"] = "*"
    return response


# 与实体信息相关
def entity(request):
    neoid = request.GET.get('id', None)
    # signal = request.GET.get('signal', None)
    # owlNeo4j.set_KB(signal)
    response = HttpResponse(json.dumps(owlNeo4j.get_entity_info_by_id(int(neoid)), ensure_ascii=False))
    response["Access-Control-Allow-Origin"] = "*"
    return response


# def test11(request):
#     s = request.GET.get('str')
#     res = {
#         "code": 0,
#         "len": len(s)
#     }
#
#     response = HttpResponse(json.dumps(res))
#
#     return response