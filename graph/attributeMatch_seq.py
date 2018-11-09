#coding=utf-8
import logging
import serviceQA
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
import jieba
import json

delete_head_words = ['（一）','（二）','（三）','（四）', '（五）', '（六）','（七）','（八）','（九）',
                    '1.','2.','3.','4.','5.','6.','7.','8.','9.',
                    '1、','2、','3、','4、','5、','6、','7、','8、','9、',
                    '(1)','(2)','(3)','(4)','(5)','(6)','(7)','(8)','(9)',
                    '一、','二、','三、','四、','五、','六、','七、','八、','九、']
sequence_list = [[u'（一）',u'（二）',u'（三）',u'（四）', u'（五）', u'（六）',u'（七）',u'（八）',u'（九）',u'（十）',u'（十一）',u'（十二）'],
                [u'1.',u'2.',u'3.',u'4.',u'5.',u'6.',u'7.',u'8.',u'9.',u'10.',u'11.',u'12.'],
                [u'1、',u'2、',u'3、',u'4、',u'5、',u'6、',u'7、',u'8、',u'9、',u'10、',u'11、',u'12、'],
                [u'(1)',u'(2)',u'(3)',u'(4)',u'(5)',u'(6)',u'(7)',u'(8)',u'(9)',u'(10)',u'(11)',u'(12)'],
                [u'一、',u'二、',u'三、',u'四、',u'五、',u'六、',u'七、',u'八、',u'九、',u'十、',u'十一、',u'十二、'],
                [u'（1）',u'（2）',u'（3）',u'（4）',u'（5）',u'（6）',u'（7）',u'（8）',u'（9）',u'（10）',u'（11）',u'（12）'],
                [u'1．',u'2．',u'3．',u'4．',u'5．',u'6．',u'7．',u'8．',u'9．',u'10．',u'11．',u'12．']]
time_list = [[u'后',u'之后',u'然后',u'除了'],[u'前',u'之前'],[u'当时']]
#从文本中提取流程性表达
def sequence_extract(content):
    seq_sen_list = []
    flag = 0
    for sequence in sequence_list:
        if sequence[0] in content:
            target_sequence = sequence
            flag = 1
            break
    if flag == 1:
        num = 0
        for i  in range(len(target_sequence)):
            num += 1
            if target_sequence[i] not in content:
                num = num -1
                break
        for i in range(num):
            if i < num-1:
                start = content.index(target_sequence[i])+len(target_sequence[i])
                end = content.index(target_sequence[i+1])
                sentence = content[start:end]
            else:
                start = content.index(target_sequence[i])+len(target_sequence[i])
                sentence = content[start:]
            seq_sen_list.append(sentence)
    if flag == 0:
        sentence_list = content.split(u'。')
        for sentence in sentence_list:
            sentence = sentence.strip()
            if len(sentence) >= 15 :
                seq_sen_list.append(sentence)
    return seq_sen_list



def answer_selection_by_attextract_TFIDF_allAttribute(seg_list, attri_value_list, answer_num=3, threshold=0.5):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，将所有属性中每句话作为字典的语料库，生成每句话的TFIDF向量，再获取每个向量中包含seg_list中的关键字的权重，相加，作为这个句子的最终的权重。
    设置阈值：分数排前三的三个句子
    问题：
    1)应该加入相似词的匹配机制
    效果：还是有误差，在没有相似词匹配的情况下，比上面的方法有提高
    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的属性完整句子
    :param answer_num: 返回答案的数目，默认是3
    :param threshold: 挑选答案的权重，默认是0.1
    :return: 得分最高的句子，具有的词数
    '''
    id2sentences = {}
    sentence2id = {}
    sentences = []
    orginal_sentence = ''.join([str(seg) for seg in seg_list])
    t = -1
    for m in range(len(time_list)):
        for time in time_list[m]:
            if orginal_sentence.find(time) != -1:
                t = m  # t表示时序，t = 0 时，表示问之后的事情；t = 1 时，表示问之前的事情；t = 2 时，表示问现在的事情
                break
    # print 't值为：',t
    id = 0
    for i in range(len(attri_value_list)):
        id2sentences[id] = attri_value_list[i]
        id += 1
    for i in range(len(id2sentences)):
        result = sequence_extract(id2sentences[i])
        id2sentences[i] = result
    for i in id2sentences:
        for sentence in id2sentences[i]:
            sentence2id[sentence] = i
            sentences.append(sentence)
    logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    attri_coupus = []
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
            #查看分词和匹配结果
    counter = CountVectorizer(lowercase=False)
    counter.fit(attri_coupus)
    counts = counter.transform(attri_coupus)
    tfidfer = TfidfTransformer()
    tfidf = tfidfer.fit_transform(counts)
    word = counter.get_feature_names()  # 获取词袋模型中的所有词语
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    sentence_and_weight = []
    for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
        sentence_weight = 0.0
        for j in range(len(word)):
            if word[j] in seg_list: #是我关心的词汇
                sentence_weight += weight[i][j]
        sentence_and_weight.append((i, sentence_weight))
    sentence_and_weight.sort(key=lambda x: x[1], reverse=True) #按照权重，从大到小排序
    max_score = 0.0
    result_sentence = ''
    if len(sentence_and_weight) >= answer_num:
        for i in range(answer_num):
              sentence = sentences[sentence_and_weight[i][0]]
              if t == 2:
                    max_sentence = sentence
              elif t == 0:
                  id = sentence2id[sentence]
                  sentences_list = id2sentences[id]
                  no = sentences_list.index(sentence)
                  max_sentence = ''
                  # for sen in sentences_list:
                  #     print sen,
                  #     print
                  if no < (len(sentences_list)-1):
                      for i in range(no+1,len(sentences_list)):
                             max_sentence += sentences_list[i]
                      # print 'step1:',max_sentence
                  else:
                      max_sentence = u'已经是办理该业务的最后一步！'
              elif t == 1 :
                  id = sentence2id[sentence]
                  sentences_list = id2sentences[id]
                  no = sentences_list.index(sentence)
                  if no != 0:
                      max_sentence = ''
                      for i in range(0,no):
                         max_sentence += sentences_list[i]
                  else:
                      max_sentence = u'已经是办理该业务的第一步！'
              else:
                  max_sentence = sentence
              # print 'step1.5:',max_sentence
              # print 'point:',sentence_and_weight[i][1]
              if sentence_and_weight[i][1] > threshold:
                 # print 'step2:',max_sentence
                 result_sentence += "候选答案"+": \t"+max_sentence+'\t\n'
    else:
        if len(sentence_and_weight) > 0:
            for i in range(len(sentence_and_weight)):
              sentence = sentences[sentence_and_weight[i][0]]
              if t == 2:
                    max_sentence = sentence
              elif t == 0:
                  id = sentence2id[sentence]
                  sentences_list = id2sentences[id]
                  no = sentences_list.index(sentence)
                  if no < (len(sentences_list)-1):
                      max_sentence = ''
                      for i in range(no+1,len(sentences_list)):
                             max_sentence += sentences_list[i]
                  else:
                      max_sentence = u'已经是办理该业务的最后一步！'
              elif t == 1 :
                  id = sentence2id[sentence]
                  sentences_list = id2sentences[id]
                  no = sentences_list.index(sentence)
                  if no != 0:
                      max_sentence = ''
                      for i in range(0,no):
                         max_sentence += sentences_list[i]
                  else:
                      max_sentence = u'已经是办理该业务的第一步！'
              else:
                  id = sentence2id[sentence]
                  sentences_list = id2sentences[id]
                  for sentence in sentences_list:
                      max_sentence += sentence
              if sentence_and_weight[i][1] > threshold:
                  result_sentence += "候选答案"+": \t"+max_sentence+'\t\n'
    if result_sentence != '' and len(result_sentence) != 0:
        for head_word in delete_head_words:
            if head_word in result_sentence:
                result_sentence = result_sentence.replace(head_word, '')
        max_score = sentence_and_weight[0][1]
    logging.info('answer:'+result_sentence)
    logging.info('point:')
    logging.info(max_score)
    # print 'answer:',result_sentence
    return {'answer':result_sentence.encode('unicode-escape'), 'point':max_score}
