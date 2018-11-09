#coding=utf-8
import json
import codecs
nodes = []
links = []
old2new = {}
new_nodes = []
new_links = []
id_num = 0
count = 0
linkid = 0
with codecs.open('new_nodes_links_2.json','r') as foo:
    data = json.load(foo)
nodes = data['nodes']
links = data['links']
for node in nodes:
    if 'taglist' not in node:
        node['taglist'] = u'分行'
        node['category'] = u'分行'
        new_nodes.append(node)
    else:
        new_nodes.append(node)
for node in new_nodes:
    oldid = int(node['id'])
    node['id'] = str(count)
    old2new[oldid] = count
    count += 1
for link in links:
   if (link['source'] in old2new) and (link['target'] in old2new):
         new_source = old2new[link['source']]
         new_target = old2new[link['target']]
         link['source'] = new_source
         link['target'] = new_target
         link['id'] = linkid
         new_links.append(link)
         linkid += 1
json_data = json.dumps({'nodes':new_nodes,'links':new_links},ensure_ascii=False)
with codecs.open('new_nodes_links_4.json','w',encoding='utf-8') as foo:
    foo.write(json_data)