# coding:utf-8
from icbckg import config
import jieba.posseg as posseg

# 分词
def segment(sentence):
    fliter_list = config.stop_words
    seg_list_unflit = list(posseg.cut(sentence))#posseg.cut返回的是一个生成器，每一项包括分词及标注
    seg_list_flit = []
    for word in seg_list_unflit:
        if word.word not in fliter_list:
            seg_list_flit.append(word)
    return seg_list_flit