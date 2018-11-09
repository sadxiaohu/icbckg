# -*- coding: UTF-8 -*-
import numpy as np
import pickle as cPickle
import jieba

default_path = './questionClassification/'

def stopwords(question):  # 去除停用词
    stopwords = set()  # 定义一个空集合
    with open(default_path+'stopwords.txt') as f:  # 将停用词库中的文本数据转换成便于处理的集合
        for _line in f:
            line = _line.strip().split(' ')
            for word in line:
                stopwords.add(word)  # 向集合中添加元素
    line = []
    for word in jieba.lcut(question.strip()):
        w = word.encode('utf-8')  # 可以省略此行
        if w not in stopwords:
            line.append(w)
    return line

def load_model(name):
    with open('%s.pkl'%name, 'rb') as fid:
            model = cPickle.load(fid)
    return model

def get_text_vec(seg_list,word2id):
    dim = len(word2id)
    text_vec = []
    vec = np.zeros(dim, dtype=np.float16)  #返回一个指定形状用零填充的数组
    for word in seg_list:   # 1-gram
        if word in word2id:
            vec[word2id[word]] = vec[word2id[word]] + 1
    for index in range(len(seg_list) - 1):    #2-gram
        if seg_list[index]+seg_list[index+1]  in word2id:
            vec[word2id[seg_list[index]+seg_list[index+1]]] += 1
    # for index in range(len(seg_list) - 2):  # 3-gram
    #     if seg_list[index] + seg_list[index + 1] + seg_list[index + 2] in word2id:
    #         vec[word2id[seg_list[index] + seg_list[index + 1]  + seg_list[index + 2]]] += 1
    text_vec.append(vec)
    return np.asarray(text_vec, dtype=np.float32)

def question_class(question):
    with open(default_path+'log_word2id.pkl','rb') as foo:
        word2id = cPickle.load(foo)
    model = load_model(default_path+'logistic')
    seg_list = stopwords(question)
    test_text_vec = get_text_vec(seg_list,word2id)
    pred = model.predict(test_text_vec)
    if pred[0] == 1:
        return 1
    else :
        return 0

# question = u'在办理B股证券业务开户时，到证券公司申请开通账户后,然后该怎么做'
# '在线支付B2C、C2C（买方）在柜台申请成为工行电子银行客户后，该怎么做'
#'公司办理在线支付，在注册成为企业网银客户后该做什么
# print question_class(question)

