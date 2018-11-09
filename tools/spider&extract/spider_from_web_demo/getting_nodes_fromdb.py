#!/usr/bin/env Python
#coding=utf-8
from py2neo import Graph #,Node,Relationship
import jieba.posseg as pseg
import json
import codecs
import time
import importlib
import sys
import pickle
import xlrd
from jieba import analyse
importlib.reload(sys)

def nodeget(nouns,outfile):#从知识库中取出excel示例实体中存在但网页信息中没有的实体信息
    graph = Graph(
        "http://10.1.1.28:7474",
        username="neo4j",
        password="123456"
    )
    nodelist = []
    neoidlist = []
    idcount = 133
    nonfound = []
    for word in nouns:
        result = graph.data("match(n:Instance) where n.name = '{}' return id(n) as id ,n".format(word))
        if len(result) != 0:
               for cons in result: #多个查询结果记录
                    if cons['id'] not in neoidlist:
                        neoidlist.append(cons['id'])
                        cons['n']['id'] = str(idcount)
                        idcount += 1
                        nodelist.append(dict(cons['n']))
        else:
            nonfound.append(word)
    json_data = json.dumps({'nodes':nodelist},ensure_ascii=False)
    with codecs.open(outfile,'a',encoding='utf-8') as foo:
        foo.write(json_data)
#    print(len(nonfound),nonfound)


def GetDataFromExcel(address):
    data = xlrd.open_workbook(address)
    table = data.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    nouns = []
    for i in range(1,nrows):
         data = table.row_values(i)[ncols-1]
         nouns.extend(data.split(','))
    return nouns


if __name__=='__main__':
    nouns1 = []
    with open('nodesfromweb.json','r',encoding='utf-8') as foo:
        data = json.load(foo)
        for word in data['nodes']:
            nouns1.append(word['name'])
    nouns2 = GetDataFromExcel(address = r'SCHEMA.xlsx')
    nouns3 = []
    for word1 in nouns2:
        for word2  in nouns1:
            if (word1 in word2) or (word2 in word1) :
                break
            if word2 == nouns1[-1]:
                nouns3.append(word1)
    nodeget(nouns3,'nodesfromdb.json')

'''
http://10.1.1.28:7474/db/data/transaction/310378/commit  "Content-Type: application/json"  -d '{{"statements":[{"statement":"match(n:Instance)-[r]->(m:Instance) where id(n)=5040268 and id(m)=9464288 with r,m,n return type(r),id(n) as from ,id(m) as to","resultDataContents":["row","graph"],"includeStats":true}]}}'
match(n:Instance)-[r]->(m:Instance) where id(n)=5040268 and id(m)=9464288 with r,m,n return type(r),id(n) as from ,id(m) as to
(e67f03b:Instance {description:"经济是价值的创造、转化与实现；人类经济活动就是创造、转化、实现价值，满足人类物质文化或精神文化生活需要的活动。经济可以定义为在有限的边缘范围内，如何获得最大的利益的一种艺术。有经世济民的含义。[1-3] ",keyId:"20838",label:"字词熟语",name:"经济",subname:"NO_SUBNAME",taglist:"词语,行业人物,经济人物,经济,社会",`中文名`:"经济",`主办单位`:"[HD]经济日报社",`主编`:"[HD]梅绍华",`出处`:"中国经济解释与重建",`出版周期`:"[HD]月刊",`外文名`:"Economy",`定义`:"物质生产,流通,交换等活动",`定义提出者`:"陈世清",`拼音`:"jīng jì",`正文语种`:"[HD]中文",`类别`:"[HD]经济"})
(f8c3ae4)-[:`出版社`]->(c827b3a)
(cdca880)-[:`出版社`]->(e1a7003)
'''