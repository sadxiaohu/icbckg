#coding=utf-8
'''
env:python2
author:lxf

'''
import logging
import serviceQA
from icbckg import config
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
import jieba
import json
import gensim

delete_head_words = ['（一）','（二）','（三）','（四）', '（五）', '（六）','（七）','（八）','（九）','（十）',
                    '1.','2.','3.','4.','5.','6.','7.','8.','9.', '10.',
                    '1、','2、','3、','4、','5、','6、','7、','8、','9、', '10、',
                    '(1)','(2)','(3)','(4)','(5)','(6)','(7)','(8)','(9)', '(10)',
                    '一、','二、','三、','四、','五、','六、','七、','八、','九、', '十、']

def answer_selection_by_strmatch(seg_list, attri_value):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，按相同词打的个数的多少进行分，选择多的,看一句话中重复的词的个数进行排序
    规则：每个属性中按'。' 进行分句，每个属性中抽取一个答案，排序时按出现的词的数目排序，多次出现相同词按多次记
    设置阈值：
    问题：不紧要的分词可能出现多次，影响精度

    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的属性完整句子
    :return: 得分最高的句子，具有的词数
    '''
    # logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    sentences = [str(sen.strip()) for sen in attri_value.split('。')]
    max_sentence = ''
    max_score = 0
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            count = 0
            for q_word in seg_list:
                for a_word in attri_wordlist:
                    if q_word == a_word:
                        count += 1
            #查看分词和匹配结果
            # logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
            # logging.info("comman words num: "+str(count))
            if max_score < count:
                max_score = count
                max_sentence = sentence
    # logging.info("max_sentence: " + max_sentence + ", max_score: " + str(max_score))
    return {'answer':max_sentence.encode('unicode-escape'), 'point':max_score*0.1}

def answer_selection_by_strmatch_set(seg_list, attri_value):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，按相同词打的个数的多少进行分，选择多的,看一句话中重复的词的个数进行排序
    规则：每个属性中按'。' 进行分句，每个属性中抽取一个答案,排序时，比较有的词的数目，多个相同词，按一个算
    设置阈值：
    问题：标点符号也进行了匹配

    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的属性完整句子
    :return: 得分最高的句子，具有的词数
    '''
    logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    sentences = [str(sen.strip()) for sen in attri_value.split('。')]
    max_sentence = ''
    max_score = 0
    for sentence in sentences:
        common_words = set()
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            for q_word in seg_list:
                for a_word in attri_wordlist:
                    if q_word == a_word:
                        common_words.add(q_word)
            #查看分词和匹配结果
            logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
            logging.info("comman words num: "+str(len(common_words)))
            if max_score < len(common_words):
                max_score = len(common_words)
                max_sentence = sentence
    logging.info("max_sentence: " + max_sentence + ", max_score: " + str(max_score))
    return {'answer':max_sentence.encode('unicode-escape'), 'point':max_score*0.1}

def answer_selection_by_attextract_TFIDF(seg_list, attri_value):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，计算每句话的相对于该段文本的TFIDF向量和，以问句分词作为词典，生成待匹配的句子的TFIDF句子向量，将句子向量求和，得到一个数，比较数字大小，排序，取最大
    返回：得分最高的句子
    设置阈值：
    问题：
    1)应该加入相似词的匹配机制
    效果：不理想，因为seg_list中的分词太少，使得每个句子的权重都是1.0
    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的所有属性的完整句子
    :return: 得分最高的句子，具有的词数
    '''
    logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    seg_corpus = [' '.join(seg_list)]
    sentences = [str(sen.strip()) for sen in attri_value.split('。')]
    attri_coupus = []
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
            #查看分词和匹配结果
            logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
    counter = CountVectorizer()
    counter.fit(seg_corpus)
    logging.info("countvectorizer words dict: ")
    logging.info(json.dumps(counter.vocabulary_, ensure_ascii=False))
    counts = counter.transform(attri_coupus)
    logging.info("one-hot vector: ")
    logging.info(counts.toarray())
    tfidfer = TfidfTransformer()
    tfidf = tfidfer.fit_transform(counts)
    logging.info("TFIDF vector: ")
    logging.info(tfidf.toarray())
    max_sentence = ''
    max_score = 0.0
    for index,vector in enumerate(tfidf.toarray()):
        sum = 0.0
        for num in vector:
            true_num = float('%.5f' % num)
            sum += true_num
        if max_score < sum:
            max_sentence = sentences[index]
            max_score = sum
    for head_word in delete_head_words:
        if head_word in max_sentence:
            max_sentence = max_sentence.replace(head_word, '')
    logging.info('answer:'+max_sentence)
    logging.info('point:')
    logging.info(max_score)
    return {'answer':max_sentence.encode('unicode-escape'), 'point':max_score}

def answer_selection_by_attextract_TFIDF_allAttribute(seg_list, attri_value_list, answer_num=3, threshold=0.1):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，一次性将所有属性中每句话作为字典的语料库，生成每句话的TFIDF向量，再获取每个向量中包含seg_list中的关键字的权重，相加，作为这个句子的最终的权重。
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
    logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    sentences = []
    for attri_value in attri_value_list:
        sentences += [str(sen.strip()) for sen in attri_value.split('。')]
    for sentence in sentences:
        if sentence == '' or len(sentence) == 0:
            sentences.remove(sentence)
    attri_coupus = []
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
            #查看分词和匹配结果
            # logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
    counter = CountVectorizer(lowercase=False)
    counter.fit(attri_coupus)
    # logging.info("countvectorizer words dict: ")
    # logging.info(json.dumps(counter.vocabulary_, ensure_ascii=False))
    counts = counter.transform(attri_coupus)
    # logging.info("one-hot vector: ")
    # logging.info(counts.toarray())
    tfidfer = TfidfTransformer()
    tfidf = tfidfer.fit_transform(counts)
    # logging.info("TFIDF vector: ")
    # logging.info(tfidf.toarray())
    word= counter.get_feature_names()  # 获取词袋模型中的所有词语
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    sentence_and_weight = []
    for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
        sentence_weight = 0.0
        for j in range(len(word)):
            if word[j] in seg_list: #是我关心的词汇
                sentence_weight += weight[i][j]
        sentence_and_weight.append((i, sentence_weight))
    sentence_and_weight.sort(key=lambda x: x[1], reverse=True) #按照权重，从大到小排序
    # logging.info(sentence_and_weight)
    max_score = 0.0
    result_sentence = ''
    if len(sentence_and_weight) >=answer_num:
        for i in range(answer_num):
            if sentence_and_weight[i][1] > threshold:
                result_sentence += "候选答案"+str(i+1)+": \t"+sentences[sentence_and_weight[i][0]]+';\t\n'
    else:
        if len(sentence_and_weight) > 0:
            for i in range(len(sentence_and_weight)):
                if sentence_and_weight[i][1] > threshold:
                    result_sentence += "候选答案"+str(i+1)+": \t"+sentences[sentence_and_weight[i][0]]+';\t\n'
    if result_sentence != '' and len(result_sentence) != 0:
        for head_word in delete_head_words:
            if head_word in result_sentence:
                result_sentence = result_sentence.replace(head_word, '')
        max_score = sentence_and_weight[0][1]
    logging.info('answer:'+result_sentence)
    logging.info('point:' + str(max_score))
    return {'answer':result_sentence.encode('unicode-escape'), 'point':max_score}

def answer_selection_by_attextract_TFIDF_allAttribute_word2vec(seg_list, attri_value_list, answer_num=3, tfidf_threshold=0.5, w2v_threshold=0.7):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，将所有属性中每句话作为字典的语料库，生成每句话的TFIDF向量，再获取每个向量中包含seg_list中的关键字的权重，相加，作为这个句子的最终的权重。
    与方法：answer_selection_by_attextract_TFIDF_allAttribute的区别是：进行了改进，使用提前训练好的word2vec向量进行关键字的匹配，对问句中有而匹配问句文本语料中没有的关键字，
    选取wrod2vec向量最相近的关键字，通过阈值：w2v_threshold控制匹配的精度
    设置阈值：分数排前三的三个句子
    问题：
    1)只对语料中没有的问句分词进行Word2vec匹配，对已有的分词也可以匹配，赋以较低的权重——通过训练能够获得最佳的参数值，比自己凭经验设置要智能和准确
    效果：还是有误差，在没有相似词匹配的情况下，比上面的方法有提高
    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的属性完整句子
    :param answer_num: 返回答案的数目，默认是3
    :param tfidf_threshold: TIIDF挑选答案的权重，默认是0.5
    :param w2v_threshold=0.8: 相对于问句中的分词，属性文本中缺失的分词的word2vec最相似词的最低匹配阈值，默认是0.7
    :return: 得分最高的句子，具有的词数
    '''
    # logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    sentences = []
    for attri_value in attri_value_list:
        sentences += [str(sen.strip()) for sen in attri_value.split('。')]
    for sentence in sentences:
        if sentence == '' or len(sentence) == 0:
            sentences.remove(sentence)
    attri_coupus = []
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
            #查看分词和匹配结果
            # logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
    counter = CountVectorizer(lowercase=False)
    counter.fit(attri_coupus)
    # logging.info("countvectorizer words dict: ")
    # logging.info(json.dumps(counter.vocabulary_, ensure_ascii=False))
    counts = counter.transform(attri_coupus)
    # logging.info("one-hot vector: ")
    # logging.info(counts.toarray())
    tfidfer = TfidfTransformer()
    tfidf = tfidfer.fit_transform(counts)
    # logging.info("TFIDF vector: ")
    # logging.info(tfidf.toarray())
    words = counter.get_feature_names()  # 获取词袋模型中的所有词语
    all_fit_wrods = []  # 属性句子中所有要抽取相加的词，包括与问句完全匹配的分词和word2vec匹配最高的词
    for seg in seg_list:
        if seg in words:
            all_fit_wrods.append(seg)
        else:
            max_fit_word = ['', w2v_threshold]  # 最匹配的词，[0]存词语，[1]存相似度
            for word in words:
                if word not in all_fit_wrods:
                    try:
                        word_similarity = config.w2v_model.similarity(seg, word)
                    except KeyError:
                        # logging.info('words:'+seg+','+word+" not in word2vec coupus bank!")
                        continue
                    if word_similarity > max_fit_word[1]:
                        max_fit_word[0] = word
                        max_fit_word[1] = word_similarity
            if max_fit_word[1] > w2v_threshold:
                logging.info('not fit seg: ' + seg + ' ;max_fit_word: '+max_fit_word[0]+" ,similarity:")
                logging.info(max_fit_word)
                all_fit_wrods.append(max_fit_word[0])
    fit_words_postions = [] #匹配的分词在语料库中的位置下标
    for index,word in enumerate(words):
        if len(fit_words_postions) == len(all_fit_wrods):
            break
        else:
            if word in all_fit_wrods:
                fit_words_postions.append(index)
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    sentence_and_weight = []
    for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
        sentence_weight = 0.0
        for j in fit_words_postions:
            sentence_weight += weight[i][j]
        if sentence_weight > tfidf_threshold:
            sentence_and_weight.append((i, sentence_weight))

    sentence_and_weight.sort(key=lambda x: x[1], reverse=True) #按照权重，从大到小排序
    # logging.info(sentence_and_weight)
    max_score = 0.0
    result_sentence = ''
    result_answer_num = answer_num if len(sentence_and_weight) > answer_num else len(sentence_and_weight)
    for i in range(result_answer_num):
        result_sentence += "候选答案"+str(i+1)+": \t"+sentences[sentence_and_weight[i][0]]+';\t\n'
    if result_sentence != '' and len(result_sentence) != 0:
        for head_word in delete_head_words:
            if head_word in result_sentence:
                result_sentence = result_sentence.replace(head_word, '')
        max_score = sentence_and_weight[0][1]
    # logging.info('answer:'+result_sentence)
    # logging.info('point:' + str(max_score))
    return {'answer':result_sentence.encode('unicode-escape'), 'point':max_score}

def answer_selection_by_TFIDF_allAttribute_word2vec_moreSubSeg(seg_list, attri_value_list, answer_num=3, tfidf_threshold=0.5, w2v_threshold=0.7, w2v_sub_threshold=0.85):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，将所有属性中每句话作为字典的语料库，生成每句话的TFIDF向量，再获取每个向量中包含seg_list中的关键字的权重，不存在的取大于阈值w2v_threshold的最相似词，
    存在的也取大于阈值w2v_sub_threshold的最相似的分词，将各句子的分词tfidf值与相似度权重相乘再相加，作为这个句子的最终的权重。
    与方法：answer_selection_by_attextract_TFIDF_allAttribute的区别是：进行了改进，进行了改进，加入已存在词的最相似词匹配机制，最后的句子包含的词越多，权重越高。
    设置阈值：分数排前三的三个句子
    效果：由于语料中的句子和问题的分词相同数目交集较小，效果不明显
    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的属性完整句子
    :param answer_num: 返回答案的数目，默认是3
    :param tfidf_threshold: TIIDF挑选答案的权重，默认是0.5
    :param w2v_threshold=0.7: 相对于问句中的分词，属性文本中缺失的分词的word2vec最相似词的最低匹配阈值，默认是0.7
    :param w2v_sub_threshold=0.85: 相对于问句中的分词，属性文本中已存在的分词的word2vec最相似词的最低匹配阈值，默认是0.85
    :return: 得分最高的句子，具有的词数
    '''
    # logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    sentences = []
    for attri_value in attri_value_list:
        sentences += [str(sen.strip()) for sen in attri_value.split('。')]
    for sentence in sentences:
        if sentence == '' or len(sentence) == 0:
            sentences.remove(sentence)
    attri_coupus = []
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
            #查看分词和匹配结果
            # logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
    counter = CountVectorizer(lowercase=False)
    counter.fit(attri_coupus)
    # logging.info("countvectorizer words dict: ")
    # logging.info(json.dumps(counter.vocabulary_, ensure_ascii=False))
    counts = counter.transform(attri_coupus)
    # logging.info("one-hot vector: ")
    # logging.info(counts.toarray())
    tfidfer = TfidfTransformer()
    tfidf = tfidfer.fit_transform(counts)
    # logging.info("TFIDF vector: ")
    # logging.info(tfidf.toarray())
    words = counter.get_feature_names()  # 获取词袋模型中的所有词语
    all_fit_wrods = []  # 属性句子中所有要抽取相加的词，包括与问句完全匹配的分词和word2vec匹配最高的词
    for seg in seg_list:
        if seg in words: #语料库中包含问题分词
            max_fit_word = ['', w2v_sub_threshold, 0]  # 最匹配的词，[0]存词语，[1]存相似度, [2]存分词在语料词典中的位置
            for index,word in enumerate(words):
                if word == seg:
                    all_fit_wrods.append([seg, 1, index])
                else:
                    try:
                        if seg not in config.w2v_model:
                            continue
                        if word not in config.w2v_model:
                            continue
                        word_similarity = config.w2v_model.similarity(seg, word)
                    except KeyError:
                        # logging.info('words:'+seg+','+word+" not in word2vec coupus bank!")
                        continue
                    if word_similarity > max_fit_word[1]:
                        max_fit_word[0] = word
                        max_fit_word[1] = word_similarity
                        max_fit_word[2] = index
            if max_fit_word[1] > w2v_sub_threshold:
                logging.info('not fit seg: ' + seg + ' ;max_fit_word: ' + max_fit_word[0] + " ,similarity:")
                logging.info(max_fit_word)
                all_fit_wrods.append(max_fit_word)
        else:
            max_fit_word = ['', w2v_threshold, 0]  # 最匹配的词，[0]存词语，[1]存相似度, [2]存分词在语料词典中的位置
            for index, word in enumerate(words):
                try:
                    if seg not in config.w2v_model:
                        break
                    if word not in config.w2v_model:
                        continue
                    word_similarity = config.w2v_model.similarity(seg, word)
                except KeyError:
                    # logging.info('words:'+seg+','+word+" not in word2vec coupus bank!")
                    continue
                if word_similarity > max_fit_word[1]:
                    max_fit_word[0] = word
                    max_fit_word[1] = word_similarity
                    max_fit_word[2] = index
            if max_fit_word[1] > w2v_threshold:
                logging.info('not fit seg: ' + seg + ' ;max_fit_word: ' + max_fit_word[0] + " ,similarity:")
                logging.info(max_fit_word)
                all_fit_wrods.append(max_fit_word)
    weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
    sentence_and_weight = []
    for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
        sentence_weight = 0.0
        for j in all_fit_wrods:
            sentence_weight += weight[i][j[2]]*j[1]
        if sentence_weight > tfidf_threshold:
            sentence_and_weight.append((i, sentence_weight))
    sentence_and_weight.sort(key=lambda x: x[1], reverse=True) #按照权重，从大到小排序
    # logging.info(sentence_and_weight)
    max_score = 0.0
    result_sentence = ''
    result_answer_num = answer_num if len(sentence_and_weight) > answer_num else len(sentence_and_weight)
    for i in range(result_answer_num):
        result_sentence += "候选答案"+str(i+1)+": \t"+sentences[sentence_and_weight[i][0]]+';\t\n'
    if result_sentence != '' and len(result_sentence) != 0:
        for head_word in delete_head_words:
            if head_word in result_sentence:
                result_sentence = result_sentence.replace(head_word, '')
        max_score = sentence_and_weight[0][1]
    # logging.info('answer:'+result_sentence)
    # logging.info('point:' + str(max_score))
    return {'answer':result_sentence.encode('unicode-escape'), 'point':max_score}

def answer_selection_by_TFIDF_allAttribute_word2vec_hasmostword(seg_list, attri_value_list, answer_num=3, tfidf_threshold=0.5, w2v_threshold=0.7, w2v_sub_threshold=0.85):
    '''
    description:从属性中抽取与问题描述最相似的句子作为答案。
    处理思路：字符串匹配，将所有属性中每句话作为字典的语料库，生成每句话的TFIDF向量，再获取每个向量中包含seg_list中的关键字的权重，不存在的取大于阈值w2v_threshold的最相似词，
    存在的也取大于阈值w2v_sub_threshold的最相似的分词，将各句子的分词tfidf值与相似度权重相乘再相加，作为这个句子的最终的权重。
    再在对句子排序时，优先包含出现分词多的句子
    与方法：answer_selection_by_attextract_TFIDF_allAttribute的区别是：进行了改进，在句子排序时，优先出现分词多的句子。
    设置阈值：分数排前三的三个句子
    问题：
    :param seg_list:提问的问句分词结果
    :param attri_value: 要寻找答案的属性完整句子
    :param answer_num: 返回答案的数目，默认是3
    :param tfidf_threshold: TIIDF挑选答案的权重，默认是0.5
    :param w2v_threshold=0.7: 相对于问句中的分词，属性文本中缺失的分词的word2vec最相似词的最低匹配阈值，默认是0.7
    :param w2v_sub_threshold=0.85: 相对于问句中的分词，属性文本中已存在的分词的word2vec最相似词的最低匹配阈值，默认是0.85
    :return: 得分最高的句子，具有的词数
    '''
    # logging.info("seg_list: " + str('/'.join([str(seg) for seg in seg_list])))
    sentences = []
    for attri_value in attri_value_list:
        sentences += [str(sen.strip()) for sen in attri_value.split('。')]
    for sentence in sentences:
        if sentence == '' or len(sentence) == 0:
            sentences.remove(sentence)
    attri_coupus = []
    for sentence in sentences:
        if sentence != '' and len(sentence) != 0:
            all_attri_wordlist = serviceQA.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
            #查看分词和匹配结果
            logging.info("sentence: "+ sentence+ ", attri_wordlist: "+ str('/'.join([str(seg) for seg in attri_wordlist])))
    try:
        counter = CountVectorizer(lowercase=False)
        counter.fit(attri_coupus)
        # logging.info("countvectorizer words dict: ")
        # logging.info(json.dumps(counter.vocabulary_, ensure_ascii=False))
        counts = counter.transform(attri_coupus)
        # logging.info("one-hot vector: ")
        # logging.info(counts.toarray())
        tfidfer = TfidfTransformer()
        tfidf = tfidfer.fit_transform(counts)
        # logging.info("TFIDF vector: ")
        # logging.info(tfidf.toarray())
        words = counter.get_feature_names()  # 获取词袋模型中的所有词语
        all_fit_wrods = []  # 属性句子中所有要抽取相加的词，包括与问句完全匹配的分词和word2vec匹配最高的词
        all_fit_segs = []  # words中包含的seg
        for seg in seg_list:
            if seg in words: #语料库中包含问题分词
                all_fit_wrods.append([seg, 1, words.index(seg)])
                all_fit_segs.append([seg, words.index(seg)])
                max_fit_word = ['', w2v_sub_threshold, 0]  # 最匹配的词，[0]存词语，[1]存相似度, [2]存分词在语料词典中的位置
                for index,word in enumerate(words):
                    if word != seg:
                        try:
                            if seg not in config.w2v_model:
                                break
                            if word not in config.w2v_model:
                                continue
                            word_similarity = config.w2v_model.similarity(seg, word)
                        except KeyError:
                            # logging.info('words:'+seg+','+word+" not in word2vec coupus bank!")
                            continue
                        if word_similarity > max_fit_word[1]:
                            max_fit_word[0] = word
                            max_fit_word[1] = word_similarity
                            max_fit_word[2] = index
                if max_fit_word[1] > w2v_sub_threshold:
                    logging.info('not fit seg: ' + seg + ' ;max_fit_word: ' + max_fit_word[0] + " ,similarity:")
                    logging.info(max_fit_word)
                    all_fit_wrods.append(max_fit_word)
            else:
                max_fit_word = ['', w2v_threshold, 0]  # 最匹配的词，[0]存词语，[1]存相似度, [2]存分词在语料词典中的位置
                for index, word in enumerate(words):
                    try:
                        if seg not in config.w2v_model:
                            break
                        if word not in config.w2v_model:
                            continue
                        word_similarity = config.w2v_model.similarity(seg, word)
                    except KeyError:
                        # logging.info('words:'+seg+','+word+" not in word2vec coupus bank!")
                        continue
                    if word_similarity > max_fit_word[1]:
                        max_fit_word[0] = word
                        max_fit_word[1] = word_similarity
                        max_fit_word[2] = index
                if max_fit_word[1] > w2v_threshold:
                    logging.info('not fit seg: ' + seg + ' ;max_fit_word: ' + max_fit_word[0] + " ,similarity:")
                    logging.info(max_fit_word)
                    all_fit_wrods.append(max_fit_word)
        weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
        sentence_and_weight = []
        for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
            sentence_weight = 0.0
            seg_exist_num = 0
            for j in all_fit_wrods: #计算TFIDF权重
                sentence_weight += weight[i][j[2]]*j[1]
            if sentence_weight > tfidf_threshold:
                for seg_info in all_fit_segs:
                    if weight[i][seg_info[1]] > 0:
                        seg_exist_num += 1
                sentence_and_weight.append((i, seg_exist_num, sentence_weight)) #0：句子索引，1：句子中包含的问句分词数，2：句子的TFIDF权重
        sentence_and_weight.sort(key=lambda x: x[1] or x[2], reverse=True) #排序：先按句子包含的分词数，再按照权重，从大到小排序
        # logging.info(sentence_and_weight)
        max_score = 0.0
        result_sentence = ''
        result_answer_num = answer_num if len(sentence_and_weight) > answer_num else len(sentence_and_weight)
        for i in range(result_answer_num):
            result_sentence += "候选答案"+str(i+1)+": \t"+sentences[sentence_and_weight[i][0]]+';\t\n'
        if result_sentence != '' and len(result_sentence) != 0:
            for head_word in delete_head_words:
                if head_word in result_sentence:
                    result_sentence = result_sentence.replace(head_word, '')
            max_score = sentence_and_weight[0][1]
        logging.info('answer:'+result_sentence)
        logging.info('point:' + str(max_score))
    except Exception as e:
        logging.info(u'发生异常：', Exception)
        return None
    return {'answer':result_sentence.encode('unicode-escape'), 'point':max_score}

def TFIDF_test():
    # reg_list = ['今天，中国芯片技术超过了世界']
    # texts = ['小明，今天中国的天气非常好啊！', '中国芯片技术落后于世界']
    reg_list = ['中B股是什么意思']
    texts = ['资金实时到账，助您及时把握B股市场的投资良机', 'B股：B股的正式名称是人民币特种股票，它是以人民币标明面值，但只能外币认购和买卖，在境内（上海、深圳）证券交易所上市交易的股票']
    rll = []
    tll = []
    for text in reg_list:
        words = [word for word in jieba.cut(text)]
        rll.append(' '.join(words))
    print(json.dumps(rll, ensure_ascii=False))

    for text in texts:
        words = [word for word in jieba.cut(text)]
        tll.append(' '.join(words))
    print(json.dumps(tll, ensure_ascii=False))
    counter = CountVectorizer()
    # counts = counter.fit_transform(rll)
    counter.fit(tll)
    print(json.dumps(u'countvectorizer词表:\n', ensure_ascii=False))
    print(json.dumps(counter.vocabulary_, ensure_ascii=False))  # countvectorizer的词汇表，有多少个，词向量就是多少维度
    counts = counter.transform(tll)
    print(json.dumps('词向量矩阵:\n', ensure_ascii=False))
    print(counts.toarray())  # fit_transform后查看具体向量
    tfidfer = TfidfTransformer()
    tfidf = tfidfer.fit_transform(counts)
    print(json.dumps('tfidf向量矩阵：\n', ensure_ascii=False))
    print(tfidf.toarray())  # fit_transform后查看具体向量矩阵

def word2vec_test():
    w2v_model = gensim.models.KeyedVectors.load_word2vec_format('../resource/word2vec/baike.vectors.bin',binary=True)
    a = '包括'
    b = '包含'
    print(type(a))
    print(type(a.decode('utf-8')))
    print(type(u'包括'))
    print(w2v_model.similarity(a.decode('utf-8'), b.decode('utf-8')))
    if 'exchange' in w2v_model:
        print(w2v_model.similarity('exchange', b.decode('utf-8')))

    # print(w2v_model.n_similarity(a, b))

if __name__=="__main__":
    # TFIDF_test()
    word2vec_test()