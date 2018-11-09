#coding=utf-8
import json
import codecs
defaultpath = r'./'

if __name__=='__main__':
    with codecs.open(defaultpath+r'\new_nodes_3.json','r',encoding='utf-8') as foo:
        data = json.load(foo)
    links = []
    idcount = 5000
    newnodes = []
    mapdict = {u'个人网上银行':[21],u'企业网上银行':[677],u'网上银行':[678],u'电话银行':[24],u'手机银行':[29],
               u'电子银行':[679],u'营业网点':[680],u'营业机构':[680],u'ATM':[681],u'自助终端':[682]
    }
    attr1 = u'服务渠道与时间'
    attr2 = u'服务渠道'
    for entity1 in data['nodes']:#给定实体集找关系
        if (attr2 in entity1) and (attr1 not in entity1):
              for key in mapdict:
                  if key in entity1[attr2]:
                      for id in mapdict[key]:
                          link = {}
                          link['id'] = idcount
                          link['name'] = '服务渠道'
                          link['source'] = int(entity1['id'])
                          link['target'] = id
                          idcount += 1
                          links.append(link)
    json_data = json.dumps({'links':links})
    print(len(links))
    with codecs.open("links_4.json",'w',encoding='utf-8') as foo:
        foo.write(json_data)