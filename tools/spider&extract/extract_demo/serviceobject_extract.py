#coding=utf-8
import json
import codecs
defaultpath = r'./'

if __name__=='__main__':
    with codecs.open(defaultpath+r'\new_nodes_2.json','r',encoding='utf-8') as foo: # 打开待处理数据集，文件名根据实际情况填写
        nodes = json.load(foo)['nodes']
    links = []
    idcount = 0
    newnodes = []
    attr = u'服务对象'  # 可换成卡片种类，发行范围，联名单位等可以作为关系的名称
    name2id = {}
    for node in nodes:
        if node['name'] not in node:
            name2id[node['name']] = node['id']
    for node in nodes:
        if int(node['id']) >= 2000:
            if attr in node:
                for name in name2id:
                    if name in node[attr] and (name != node['name']):
                          link = {}
                          link['id'] = idcount
                          link['name'] = attr
                          link['source'] = int(node['id'])
                          link['target'] = int(name2id[name])
                          idcount += 1
                          links.append(link)
    json_data = json.dumps({'nodes':links})
    print(len(links))
    with codecs.open("links_2.json",'w',encoding='utf-8') as foo:
        foo.write(json_data)
