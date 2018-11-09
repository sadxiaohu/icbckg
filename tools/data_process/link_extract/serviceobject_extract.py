#coding=utf-8
import json
import codecs
defaultpath = r'./'

if __name__=='__main__':
    with codecs.open(defaultpath+r'\new_nodes_4.json','r',encoding='utf-8') as foo:
        nodes = json.load(foo)['nodes']
    links = []
    idcount = 4000
    newnodes = []
    attr = u'服务对象'
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
                          link['name'] = '服务对象'
                          link['source'] = int(node['id'])
                          link['target'] = int(name2id[name])
                          idcount += 1
                          links.append(link)
    json_data = json.dumps({'nodes':links})
    print(len(links))
    with codecs.open("links_3.json",'w',encoding='utf-8') as foo:
        foo.write(json_data)
