# -*- coding: UTF-8 -*-
'''
authour:lxf
env:python2
目的：将新爬取的数据融合到原来的知识库文件
'''
import json
import codecs

origin_bank_path = '../resource/kg/nodes_links_8.json'
kb = json.load(codecs.open(origin_bank_path, 'r', encoding='utf-8'))
new_bank_path = './sub_bank.json'
merged_bank_path = '../resource/kg/new_nodes_links.json'

def get_max_id_in_nodes():
    ids = [int(node['id']) for node in kb['nodes']]
    return max(ids)

def get_max_id_in_links():
    ids = [int(link['id']) for link in kb['links']]
    return max(ids)

new_node_id = int(get_max_id_in_nodes())+1
new_link_id = int(get_max_id_in_links())+1
pointer_current_bank = 0
all_nodes = []
all_links = []
with codecs.open(new_bank_path, 'r', encoding='utf-8') as rf:
    # all_nodes = json.load(rf)
    print(len(all_nodes))
    for node in all_nodes:
        if node['category'] == u'分行':
            pointer_current_bank = new_node_id
            node['id'] = pointer_current_bank
            new_node_id += 1
        else:
            node['id'] = new_node_id
            new_node_id += 1
            new_link = {"id":new_link_id,
                        "name":node['taglist'].strip().split(',')[-1],
                        "source":pointer_current_bank,
                        "target":node['id']}
            new_link_id += 1
            all_links.append(new_link)
    kb['nodes'] += all_nodes
    kb['links'] += all_links
    with codecs.open(merged_bank_path, 'w', encoding='utf-8') as wf:
        json.dump(kb, wf, ensure_ascii=False)