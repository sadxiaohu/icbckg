#coding=utf-8
#python3
import json
import codecs
from py2neo import Graph
def nodeget():  # 从知识库中取出excel示例实体中存在但网页信息中没有的实体信息
    graph = Graph(
        "http://127.0.0.1:7474",
        username="neo4j",
        password="123456"
    )
    with codecs.open('new_nodes_links_4.json','r',encoding='utf-8') as foo:
            nodes = json.load(foo)['nodes']
    with codecs.open('new_nodes_links_4.json','r',encoding='utf-8') as foo:
            links = json.load(foo)['links']
    for node in nodes: # onebyone建立节点  建立新节点样例：graph.data("create(n:pers{name:'guo',gender:'male',age:'25',id:8}) ")  # neo4j实体查询语句，此处查询实体名为word的实体
      CQL = "create(n:Instancebracket"
      for key in node:
          value = node[key].replace("'",'').replace("\\","\\\\")
          for char in key:
              if ord(char) == 32:
                  key = key.replace(' ','')
                  # print(node['id'],key,32)
                  break
          # if ' ' in key: #ascii为160空格
          #     #key = key.replace(' ','')
          #     print(node['id'],key,160)
          # if '—' in key:
          #     #key = "`"+key+"`"
          #     print(node['id'],key,'—')
          # if ord(key[0]) >=48 and ord(key[0])<=57:
          key = "`"+key+"`"
          CQL = CQL+key+":"
          CQL = CQL+"'{}'".format(value)+','
      CQL = CQL[0:-1]+'})'
      CQL = CQL.replace('bracket','{')
      graph.data(CQL)
    for link in links: #onebyone建立关系
        source_id = str(link['source'])
        target_id = str(link['target'])
        relation = str(link['name'])
        link_id = '{linkid:'+str(link['id'])+'}'
        query =    '''match(n)where n.id='{}'
                      match(m)where m.id='{}'
                      create (n)-[r:{}{}]->(m) '''.format(source_id,target_id,relation,link_id)
        graph.data(query)
nodeget()
'''
create(n:Instance{category:'电子银行',95588常用快拨码:'一级菜单二级菜单'})
match(n)
delete n
match(n)where n.id="0"
match(m)where m.id="880"
create (n)-[r:"服务对象"]->(m)
'''