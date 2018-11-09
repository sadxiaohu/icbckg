#coding=utf-8
#author:lxf
#python3

import json
import codecs
import importlib
import sys
from jieba import analyse

if __name__ == '__main__':
    dataFile = "../resource/webPages/data-all.json"
    outFile = "../resource/webPages/ayalysisResult.txt"
    entitiesNames = {}
    with open(dataFile, 'r', encoding='utf-8') as foo:
        nodes = json.load(foo)['nodes']
        for node in nodes:
            if node['name'] in entitiesNames.keys():
                entitiesNames[node['name']].append(node['id'])
            else:
                entitiesNames[node['name']] = [node['id']]

    entitiesNames = sorted(entitiesNames.items(), key=lambda d: len(d[1]), reverse=True)

    with open(outFile, 'w', encoding='utf-8') as outFile:
        outFile.write(entitiesNames.__str__())