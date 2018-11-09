#!/usr/bin/env Python
#coding=utf-8
#python3
import json
import codecs
import importlib
import sys
from jieba import analyse
importlib.reload(sys)

def trans_id(infile):#筛选实体属性
    newnodes = []
    with open(infile,'r',encoding='utf-8') as foo:
        nodes = json.load(foo)['nodes']
        for node in nodes:
            if 'taglist' in node:
                del node['taglist']
            if 'label' in node:
                del node['label']
            if 'taglist' in node:
                del node['taglist']
            if 'keyId' in node:
                del node['keyId']
            node['id'] = str(int(node['id'])-60)
            newnodes.append(node)
    data = json.dumps({'nodes':newnodes})
    with open('newnodes-all-new.json','w',encoding='utf-8') as foo:
        foo.write(data)


if __name__=='__main__':
    trans_id('newnodes-all.json')
    nouns1 = []
    with open('newnodes-all-new.json','r',encoding='utf-8') as foo:
        data = json.load(foo)
        for word in data['nodes']:
            nouns1.append(word['name'])
    print(nouns1)
    links = []
    idcount = 0
    for entity1 in data['nodes']:#利用关键词匹配建立关系，如果某个实体的某个属性对应的属性值的文本描述所提取出来的关键词（tf-idf），包含了另外实体的名称，那么从本实体建立一个关系到对应的实体，关系名为属性名。但是结果一般。
        for attr in entity1:
           keywordlist = analyse.extract_tags(entity1[attr])
           for entity2 in data['nodes']:
              link = {}
              if entity2['name'] in keywordlist:
                  if entity1['id'] != entity2['id'] and attr != 'name' and attr != 'description':
                      link['id'] = idcount
                      link['name'] = attr
                      link['source'] = int(entity1['id'])
                      link['target'] = int(entity2['id'])
                      idcount += 1
                      links.append(link)
    json_data = json.dumps({'links':links})
    #print(len(links))
    with codecs.open("links.json",'w',encoding='utf-8') as foo:
        foo.write(json_data)
    foo = open('newnodes-all-new.json','r',encoding='utf-8')
    nodes = json.load(foo)['nodes']
    json_data = json.dumps({'nodes':nodes,'links':links})
    with codecs.open('nodes_links.json','w',encoding='utf-8') as foo:
         foo.write(json_data)
'''
http://10.1.1.28:7474/db/data/transaction/310378/commit  "Content-Type: application/json"  -d '{{"statements":[{"statement":"match(n:Instance)-[r]->(m:Instance) where id(n)=5040268 and id(m)=9464288 with r,m,n return type(r),id(n) as from ,id(m) as to","resultDataContents":["row","graph"],"includeStats":true}]}}'
match(n:Instance)-[r]->(m:Instance) where id(n)=5040268 and id(m)=9464288 with r,m,n return type(r),id(n) as from ,id(m) as to
(e67f03b:Instance {description:"经济是价值的创造、转化与实现；人类经济活动就是创造、转化、实现价值，满足人类物质文化或精神文化生活需要的活动。经济可以定义为在有限的边缘范围内，如何获得最大的利益的一种艺术。有经世济民的含义。[1-3] ",keyId:"20838",label:"字词熟语",name:"经济",subname:"NO_SUBNAME",taglist:"词语,行业人物,经济人物,经济,社会",`中文名`:"经济",`主办单位`:"[HD]经济日报社",`主编`:"[HD]梅绍华",`出处`:"中国经济解释与重建",`出版周期`:"[HD]月刊",`外文名`:"Economy",`定义`:"物质生产,流通,交换等活动",`定义提出者`:"陈世清",`拼音`:"jīng jì",`正文语种`:"[HD]中文",`类别`:"[HD]经济"})
(f8c3ae4)-[:`出版社`]->(c827b3a)
(cdca880)-[:`出版社`]->(e1a7003)
'''