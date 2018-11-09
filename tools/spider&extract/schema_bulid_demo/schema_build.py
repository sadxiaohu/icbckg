#coding=utf-8
#本脚本根据结点的taglist自动构建schema
import codecs
import json
import sys
import pickle
defaultpath = sys.path[0]+'\data'
tag2id = {}
id = 1  # id为0是根节点，tag节点的id从1开始
rootnode = ('根节点',0,0,-1)  # 根节点层号为0，tag节点从1开始，根节点的父节点为本身
schema = []
schema.append(rootnode)
schemanode = []
repnode = set()
with codecs.open(defaultpath+r'\schema.txt','r',encoding='utf-8') as foo:  # 统计在schema中重复出现的词 schema为未考虑重复词先行生成的架构
    for line in foo:
        word = line.replace('(','').replace(')','').replace("'",'').split(',')[0]
        if word not in schemanode:
            schemanode.append(word)
        else:
            repnode.add(word)
repnode = list(repnode)
print(repnode)
with codecs.open(defaultpath+r'\nodesfromicbc-new.json','r',encoding='utf-8') as foo:
    nodes = json.load(foo)['nodes']
for node in nodes:  # 建立tag到id的映射表,解决重名映射的方法是将当前标签和上一个标签连接起来作为新的标签，并产生新的id
    taglist = node['taglist'].replace(' ','').split(',')
    for tag in taglist:
        if tag in repnode:
              num = taglist.index(tag)
              if num == 0:
                 tag = tag
              else:
                 tag = taglist[num-1]+tag
        if tag not in tag2id:
              tag2id[tag] = id
              id += 1
with open('tag2id.pkl','wb') as foo:
    pickle.dump(tag2id,foo)
with open('repnode.pkl','wb') as foo:
    pickle.dump(repnode,foo)
with open('repnode.pkl','rb') as foo:
    repnode = pickle.load(foo)
with open('tag2id.pkl','rb') as foo:
    tag2id = pickle.load(foo)
with codecs.open(defaultpath+r'\nodesfromicbc-new.json','r',encoding='utf-8') as foo:
    nodes = json.load(foo)['nodes']
for node in nodes:#构造一个树形结构的schema，每个nodeinfo分别为（标签名，标签id,层id,父标签id）
    taglist = node['taglist'].replace(' ','').split(',')
    for index in range(len(taglist)):
        tagname = taglist[index]
        layerid = index+1
        if tagname not in repnode:
            tagid = tag2id[tagname]
            if index == 0:
                fathernodeid = 0
            elif index == 1:
                fathernodeid = tag2id[taglist[0]]
            else:
                comp = taglist[index-2]+taglist[index-1]
                if comp in tag2id:
                    fathernodeid = tag2id[comp]
                else:
                    fathernodeid = tag2id[taglist[index-1]]
        else:
            if index == 0:
                fathernodeid = 0
                tagid = tag2id[tagname]
            elif index == 1:
                comp = taglist[0]+taglist[1]
                fathernodeid = tag2id[taglist[0]]
                tagid = tag2id[comp]
            else:
                comp = taglist[index-1]+taglist[index]
                tagid = tag2id[comp]
                comp1 = taglist[index-2]+taglist[index-1]
                if comp1 in tag2id:
                    fathernodeid = tag2id[comp1]
                else:
                    fathernodeid = tag2id[taglist[index-1]]
        nodeinfo = (tagname,tagid,layerid,fathernodeid)
        schema.append(nodeinfo)
schema = list(set(schema))
schema = sorted(schema,key = lambda x:(x[2],x[3]))
with codecs.open(defaultpath+r'\schema-new.txt','w',encoding='utf-8') as foo:
    for node in schema:
        foo.write(str(node)+'\n')