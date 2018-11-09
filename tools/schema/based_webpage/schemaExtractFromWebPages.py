#coding=utf-8
#author:lxf
#python3
#用途：通过网站的目录层次结构生成schema

import json
import codecs
import importlib
import sys
from jieba import analyse
import queue

def findChildren(pid):
    global tagList
    reList = []
    for tag in tagList:
        if tag[2] == pid:
            reList.append((tag[0], tag[1]))

    return reList


if __name__ == '__main__':
    sourceFile = '../resource/schema/schema-3.txt'

    outFile = '../static/json/schema_category_from_web_pages.json'

    #借助队列实现广度优先搜索
    schemaDic = {}
    searchQueue = queue.Queue()#定义一个队列
    tagList = []
    with open(sourceFile, 'r', encoding='utf-8') as sf:
        lines = sf.readlines()
        for line in lines:
            line = line.strip('()')
            line = line.replace(')','').replace("'",'')
            list = line.split(',')
            tagList.append((list[0],list[1].strip(),list[3].strip()))

    schemaDic['name'] = tagList[0][0]
    searchQueue.put((schemaDic, tagList[0][1]))#将数据放入队列中
    while not searchQueue.empty():#从队列中取数据
        current = searchQueue.get()
        childrenList = findChildren(current[1])
        if childrenList.__len__():
            current[0]['children'] = [{'name':child[0]} for child in childrenList]
            for i in range(current[0]['children'].__len__()):
                searchQueue.put((current[0]['children'][i], childrenList[i][1]))
        else:
            current[0]['value'] = 1


    with open(outFile, 'w', encoding='utf-8') as of:
        json.dump(schemaDic, of, ensure_ascii=False)