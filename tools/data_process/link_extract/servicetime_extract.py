#coding=utf-8
import json
import codecs
import re
defaultpath = './'


if __name__=='__main__':
    with codecs.open(defaultpath+r'\new_nodes_2.json','r',encoding='utf-8') as foo:
        data = json.load(foo)
    links = []
    idcount = 905
    newnodes = []
    timedict = [u'7X24',u'7x24',u'7*24']
    newnodes = []
    timedict = [u'7X24',u'7x24',u'7*24',u'7×24']
    attr1 = u'服务渠道与时间'
    attr2 = u'服务时间'
    count = 0
    pattern1 = r"[周|星期][一二三四五六日][~|至|到|-][周|星期][一二三四五六日]\d*[:|：]?\d*[-|－|到|至|~]?\d*[:|：]?\d*"
    for entity1 in data['nodes']:#从服务渠道与时间中提取时间
        if int(entity1['id']) >=246000:
            if attr1 in entity1:
                  print 'OK'
                  entity1[attr2] = ''
                  flag = 0
                  for key in timedict:
                      if key in entity1[attr1]:
                          print 'OK'
                          flag = 1
                          entity1[attr2] = "7*24小时全天候"
                          break
                  if flag == 0:
                      it = re.finditer(pattern1,entity1[attr1])
                      for match in it:
                          entity1[attr2] += match.group()
                      if entity1[attr2] != '':
                          print 'OK'
                          count += 1
                  newnodes.append(entity1)
            else:
                newnodes.append(entity1)
    json_data = json.dumps({'nodes':newnodes})
    print(count)
    print(len(newnodes))
    with codecs.open("new_nodes_3.json",'w',encoding='utf-8') as foo:
        foo.write(json_data)

'''
http://10.1.1.28:7474/db/data/transaction/310378/commit  "Content-Type: application/json"  -d '{{"statements":[{"statement":"match(n:Instance)-[r]->(m:Instance) where id(n)=5040268 and id(m)=9464288 with r,m,n return type(r),id(n) as from ,id(m) as to","resultDataContents":["row","graph"],"includeStats":true}]}}'
match(n:Instance)-[r]->(m:Instance) where id(n)=5040268 and id(m)=9464288 with r,m,n return type(r),id(n) as from ,id(m) as to
(e67f03b:Instance {description:"经济是价值的创造、转化与实现；人类经济活动就是创造、转化、实现价值，满足人类物质文化或精神文化生活需要的活动。经济可以定义为在有限的边缘范围内，如何获得最大的利益的一种艺术。有经世济民的含义。[1-3] ",keyId:"20838",label:"字词熟语",name:"经济",subname:"NO_SUBNAME",taglist:"词语,行业人物,经济人物,经济,社会",`中文名`:"经济",`主办单位`:"[HD]经济日报社",`主编`:"[HD]梅绍华",`出处`:"中国经济解释与重建",`出版周期`:"[HD]月刊",`外文名`:"Economy",`定义`:"物质生产,流通,交换等活动",`定义提出者`:"陈世清",`拼音`:"jīng jì",`正文语种`:"[HD]中文",`类别`:"[HD]经济"})
(f8c3ae4)-[:`出版社`]->(c827b3a)
(cdca880)-[:`出版社`]->(e1a7003)
'''