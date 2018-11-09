#coding=utf-8
#本脚本自动赋予schema每个根节点应具备的属性
import codecs
import json
import sys
import pickle
defaultpath = sys.path[0]+'\data'
tag2id = {}
repnode = set()
with open('repnode.pkl','rb') as foo:
    repnode = pickle.load(foo)
with open('tag2id.pkl','rb') as foo:
    tag2id = pickle.load(foo)
attrdict = {}
with codecs.open(defaultpath+r'\nodesfromicbc-new.json','r',encoding='utf-8') as foo:
    nodes = json.load(foo)['nodes']
for node in nodes:
    keys = list(node.keys())
    taglist = node['taglist'].replace(' ','').split(',')
    targtag = taglist[-1]
    if targtag in repnode:
        if len(taglist) > 1:
            id = tag2id[taglist[-2]+targtag]
            if id not in attrdict:
                 attrdict[id] = keys
            else :
                 attrdict[id].extend(keys)
        else :
            id = tag2id[targtag]
            if id  not in attrdict:
                attrdict[id] = keys
            else :
                attrdict[id].extend(keys)
    else:
        id = tag2id[targtag]
        if id not in attrdict:
          attrdict[id] = keys
        else:
          attrdict[id].extend(keys)
parentid = []
with codecs.open(defaultpath+r'\schema-new.txt','r',encoding='utf-8') as foo:
        lines = foo.readlines()
        for line in lines:
            line = line.strip('()')
            line = line.replace(')','').replace("'",'')
            id_list = line.split(',')
            parentid.append(int(id_list[3].strip()))
keylist = list(attrdict.keys())
for key in keylist:
        if key not in parentid:
           attrdict[key] = set(attrdict[key])
        else:
           del attrdict[key]
attrdict = sorted(attrdict.items(),key =lambda x:x[0])
with codecs.open(defaultpath+r'\id2attr-new.txt','w',encoding='utf-8') as foo:
    for word in attrdict:
      foo.write(str(word[0])+'\t'+str(word[1])+'\n')