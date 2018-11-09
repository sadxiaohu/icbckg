#coding=utf-8
import json
import codecs
defaultpath = './'
with codecs.open('new_nodes_2.json','r',encoding='utf-8') as foo:
    nodes = json.load(foo)['nodes']
# 特色业务与最新业务
branchbank2id = {}
for node in nodes:
    if int(node['id']) >= 247001:
        if node['name'].find(u'分行') != -1 and len(node['name']) <= 7:
            branchbank2id[node['name']] = int(node['id'])
#count = 0
# for branch in branchbank2id:
#    count += 1
#     print branch,branchbank2id[branch]
#print count
links = []
id = 2000
for node in nodes:
   if int(node['id']) >= 247001:
    if 'category' in node:
        if node['category'] == u'最新业务':
            link = {}
            branch = node['taglist'].split(',')[0]
            source = branchbank2id[branch]
            target = node['id']
            link['source'] = source
            link['target'] = int(target)
            link['id'] = id
            link['name'] = u'最新业务'
            links.append(link)
            id += 1
        if node['category'] == u'特色业务':
            link = {}
            branch = node['taglist'].split(',')[0]
            source = branchbank2id[branch]
            target = int(node['id'])
            link['source'] = source
            link['target'] = target
            link['id'] = id
            link['name'] = u'特色业务'
            links.append(link)
            id += 1
json_data = json.dumps({"links":links})
with codecs.open('links_1.json','w',encoding='utf-8') as foo:
    foo.write(json_data)