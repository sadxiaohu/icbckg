#!/usr/bin/env python
# -*- coding: utf-8 -*-

import icbckg.config as config


print ("Loading model:word2vec ......")
model = config.w2v_model


# 获取两个单词列表的相似度
def get_similarity(seg_list, word_list):

    if ("".join(seg_list) == u'是什么') and ("".join(word_list) in [u'业务简述', u'业务简介', u'产品简介', u'卡片简介', u'功能定义', 'description']):
        return 0.9

    ws1 = []
    ws2 = []
    point = 0

    for word in seg_list:
        if word in model:
            ws1.append(word)
    for word in word_list:
        if word in model:
            ws2.append(word)
    if len(ws1) > 0 and len(ws2) > 0:
        point = model.n_similarity(ws1, ws2)

    return point
