# coding:utf-8
"""
env:python2
author:lxf
"""
from searchIndex import searchEngine
import logging
import json

#搜索引擎实体
print("Loading model:Content TFIDF Vector ......")

searchEngine = searchEngine.searchEngine()

delete_head_words = ['（一）','（二）','（三）','（四）', '（五）', '（六）','（七）','（八）','（九）','（十）',
                    '1.','2.','3.','4.','5.','6.','7.','8.','9.', '10.',
                    '1、','2、','3、','4、','5、','6、','7、','8、','9、', '10、',
                    '(1)','(2)','(3)','(4)','(5)','(6)','(7)','(8)','(9)', '(10)',
                    '一、','二、','三、','四、','五、','六、','七、','八、','九、', '十、']


def find_answer_in_text_bank(seg_list, answer_num=3, pick_threshold=0.1, return_threshold=0.7):
    '''
    description:对于问句中找不到实体的情形，从全体实体属性文本中检索答案
    处理思路：将全部实体的属性信息提前训练出一个TFIDF矩阵，当问句来时，匹配问句中的分词，获取问句中分词的权重之和，作为句子的权重，进行排序，取answer_num的答案作为输出
    设置阈值：分数排前三的三个句子，进行合并
    存在问题：
    1)应该加入相似词的匹配机制
    2)应该判断句子的类型：是取前几个答案输出，还是取所有的，取所有的应该以一种什么样的形式
    效果：
    :param seg_list:提问的问句分词结果
    :param answer_num: 返回答案的数目，默认是3
    :param pick_threshold: 挑选答案的权重阈值，默认是0.1
    :param return_threshold: 大于此阈值的答案全部返回，默认为0.7，优先级高于answer_num
    :return: 得分最高的句子的合并
    '''
    sentences = searchEngine.sentences
    sentence_and_weight = searchEngine.search_relate_content_TFIDF_word2vec(seg_list, w2v_threshold=0.7)
    max_score = 0.0
    result_sentence = ''
    if return_threshold:
        for index,item in enumerate(sentence_and_weight):
            if float(item[1]) > return_threshold:
                result_sentence += "候选答案" + str(index + 1) + ": \t" + sentences[item[0]] + ';\t\n'
    elif answer_num:
        for i in range(answer_num):
            if sentence_and_weight[i][1] > pick_threshold:
                result_sentence += "候选答案" + str(i + 1) + ": \t" + sentences[sentence_and_weight[i][0]] + ';\t\n'
    if result_sentence != '' and len(result_sentence) != 0: #去除答案中的序号
        for head_word in delete_head_words:
            if head_word in result_sentence:
                result_sentence = result_sentence.replace(head_word, '')
        max_score = sentence_and_weight[0][1]
    # logging.info('answer:' + result_sentence)
    # logging.info('point:' + str(max_score))
    return {'answer': result_sentence.encode('unicode-escape'), 'point': max_score}