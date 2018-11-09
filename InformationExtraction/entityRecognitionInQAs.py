#coding=utf-8
#author:lxf
#python3

import json
import codecs
import importlib
import sys
import jieba

if __name__ == '__main__':
    inFilePath = ['../resource/questionsAndAnswers/personalfinance.txt',
                  '../resource/questionsAndAnswers/enterprisebank.txt',
                  '../resource/questionsAndAnswers/investment.txt',
                  '../resource/questionsAndAnswers/otherbusiness.txt',
                  '../resource/questionsAndAnswers/personalbank.txt']

    outFilePath = '../resource/questionsAndAnswers/outEntitiesFromQAs-1gram.txt'
    entitiesFromA2Q = {} #从回答的分词中比对问题的分词
    entitiesFromQ2A = {} #从问题的分词中比对回答的分词
    stopwords = set()
    with codecs.open('../resource/questionsAndAnswers/stopwords.txt','r',encoding='utf-8') as f:#将停用词库中的文本数据转换成便于处理的集合
        for _line in f:
            line = _line.strip().split(' ')
            for word in line:
                stopwords.add(word) #向集合中添加元素
    for file in inFilePath:
        with open(file, 'r', encoding='utf-8') as inFile:
            for line in inFile.readlines():
                rowAns = []
                rowQue = []
                question = line.split('？')[0].replace('\n','').replace('\t','')
                answer = line.split('？')[1].replace('\n','').replace('\t','')
                keywordlistInA = jieba.lcut(answer)
                for keyword in keywordlistInA:
                    if keyword not in stopwords:
                        rowAns.append(keyword)
                for index in range(len(rowAns)):       #1-gram
                    if rowAns[index] not in entitiesFromA2Q:
                        entitiesFromA2Q[rowAns[index]] = 1
                    else :
                        entitiesFromA2Q[rowAns[index]] += 1
                # for index in range(len(rowAns) - 1):    #2-gram
                #     if rowAns[index]+rowAns[index+1] not in entitiesFromA2Q:
                #         entitiesFromA2Q[rowAns[index]+rowAns[index+1]] = 1
                #     else:
                #         entitiesFromA2Q[rowAns[index]+rowAns[index+1]] += 1
                # for index in range(len(rowAns) - 2):   #3-gram
                #     if rowAns[index]+rowAns[index+1]+rowAns[index+2] not in entitiesFromA2Q:
                #         entitiesFromA2Q[rowAns[index]+rowAns[index+1]+rowAns[index+2]] = 1
                #     else:
                #         entitiesFromA2Q[rowAns[index]+rowAns[index+1]+rowAns[index+2]] += 1
                keywordlistInQ = jieba.lcut(question)
                for keyword in keywordlistInQ:
                    if keyword not in stopwords:
                        rowQue.append(keyword)
                for index in range(len(rowQue)):       #1-gram
                    if rowQue[index] not in entitiesFromQ2A:
                        entitiesFromQ2A[rowQue[index]] = 1
                    else :
                        entitiesFromQ2A[rowQue[index]] += 1
                # for index in range(len(rowQue) - 1):    #2-gram
                #     if rowQue[index]+rowQue[index+1] not in entitiesFromQ2A:
                #         entitiesFromQ2A[rowQue[index]+rowQue[index+1]] = 1
                #     else:
                #         entitiesFromQ2A[rowQue[index]+rowQue[index+1]] += 1
                # for index in range(len(rowQue) - 2):   #3-gram
                #     if rowQue[index]+rowQue[index+1]+rowQue[index+2] not in entitiesFromQ2A:
                #         entitiesFromQ2A[rowQue[index]+rowQue[index+1]+rowQue[index+2]] = 1
                #     else:
                #         entitiesFromQ2A[rowQue[index]+rowQue[index+1]+rowQue[index+2]] += 1

    entitiesFromA2Q = sorted(entitiesFromA2Q.items(), key=lambda d: d[1], reverse=True)  # sort by dict value
    entitiesFromQ2A = sorted(entitiesFromQ2A.items(), key=lambda d: d[1], reverse=True)  # sort by dict value

    with open(outFilePath, 'w', encoding='utf-8') as outFile:
        outFile.write("从回答的分词中比对问题的分词提取实体："+"\n")
        outFile.write(entitiesFromA2Q.__len__().__str__()+"\n")
        outFile.write(entitiesFromA2Q.__str__()+"\n")
        outFile.write("从问题的分词中比对回答的分词提取实体：\n")
        outFile.write(entitiesFromQ2A.__len__().__str__()+"\n")
        outFile.write(entitiesFromQ2A.__str__()+"\n")

    dataFile = "../resource/webPages/nodes_links_7.json"
    entitiesNames = set([])
    findEntitiesA = {}
    findEntitiesQ = {}
    with open(dataFile, 'r', encoding='utf-8') as foo:
        nodes = json.load(foo)['nodes']
        for node in nodes:
            entitiesNames.add(node['name'])
        print(entitiesNames.__len__())
        print(entitiesNames)
        for en in entitiesFromA2Q:
            if en[0] in entitiesNames:
                findEntitiesA[en[0]] = en[1]
        for en in entitiesFromQ2A:
            if en[0] in entitiesNames:
                findEntitiesQ[en[0]] = en[1]

    with open(outFilePath, 'a', encoding='utf-8') as outFile:
        outFile.write("从回答中可连接到的实体数目："+"\n")
        outFile.write(findEntitiesA.__len__().__str__()+"\n")
        outFile.write(findEntitiesA.__str__()+"\n")
        outFile.write("从问题中可连接到的实体数目："+"\n")
        outFile.write(findEntitiesQ.__len__().__str__()+"\n")
        outFile.write(findEntitiesQ.__str__()+"\n")




