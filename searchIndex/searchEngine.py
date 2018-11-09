#coding=utf-8
#author:lxf
from sklearn.feature_extraction.text import CountVectorizer,TfidfTransformer
from nlp import segment
import icbckg.config as config
import logging
import createDataBank
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class searchEngine:
    words = []
    weight = None
    sentences = []

    def __init__(self): #初始化搜索引擎类
        print('Loading searchEngine .......')
        createDataBank.create_bank_from_KB_file(config.KB_path, out_all_content_file_path=config.resource_path+"/indexBank/allContent")
        allContent = config.all_content
        # logging.info('serchEngine-allContent:' + allContent)
        sentences = [str(sen.strip()) for sen in allContent.split('。')]
        # logging.info('serchEngine-sentences:' + json.dumps(sentences[0], encoding='utf-8', ensure_ascii=False))
        for sentence in sentences:
            if sentence == '' or len(sentence) == 0:
                sentences.remove(sentence)
        attri_coupus = []
        for sentence in sentences:
            all_attri_wordlist = segment.segment(sentence)
            attri_wordlist = [str(word.word) for word in all_attri_wordlist]
            attri_coupus.append(' '.join(attri_wordlist))
        # logging.info('attri_coupus:' + json.dumps(attri_coupus[:10], encoding='utf-8', ensure_ascii=False))
        counter = CountVectorizer(lowercase=False)
        counter.fit(attri_coupus)
        counts = counter.transform(attri_coupus)
        tfidfer = TfidfTransformer()
        tfidf = tfidfer.fit_transform(counts)
        self.sentences = sentences
        self.words = counter.get_feature_names()  # 获取词袋模型中的所有词语
        self.weight = tfidf.toarray()  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重

    def search_relate_content_TFIDF(self, seg_list, ): #基于TFIDF匹配与问句最相似地语句
        all_fit_wrods = []  # 属性句子中所有要抽取相加的词
        for seg in seg_list:
            if seg in self.words:
                all_fit_wrods.append(seg)
        fit_words_postions = []  # 匹配的分词在语料库中的位置下标
        for index, word in enumerate(self.words):
            if len(fit_words_postions) == len(all_fit_wrods):
                break
            else:
                if word in all_fit_wrods:
                    fit_words_postions.append(index)
        sentence_and_weight = []
        for i in range(len(self.weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
            sentence_weight = 0.0
            for j in fit_words_postions:
                sentence_weight += self.weight[i][j]
            sentence_and_weight.append((i, sentence_weight))
        sentence_and_weight.sort(key=lambda x: x[1], reverse=True)  # 按照权重，从大到小排序
        return sentence_and_weight

    def search_relate_content_TFIDF_word2vec(self, seg_list, w2v_threshold): #对属性语句文本中缺失的问句分词通过word2vec匹配查找最相似地关键词
        all_fit_wrods = []  # 属性句子中所有要抽取相加的词
        for seg in seg_list:
            if seg in self.words:
                all_fit_wrods.append(seg)
            else:
                max_fit_word = ['', w2v_threshold]  # 最匹配的词，[0]存词语，[1]存相似度
                for word in self.words:
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
                    logging.info('not fit seg: ' + seg + ' ;max_fit_word: ' + max_fit_word[0] + " ,similarity:")
                    logging.info(max_fit_word)
                    all_fit_wrods.append(max_fit_word[0])
        fit_words_postions = []  # 匹配的分词在语料库中的位置下标
        for index, word in enumerate(self.words):
            if len(fit_words_postions) == len(all_fit_wrods):
                break
            else:
                if word in all_fit_wrods:
                    fit_words_postions.append(index)
        sentence_and_weight = []
        for i in range(len(self.weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
            sentence_weight = 0.0
            for j in fit_words_postions:
                sentence_weight += self.weight[i][j]
            sentence_and_weight.append((i, sentence_weight))
        sentence_and_weight.sort(key=lambda x: x[1], reverse=True)  # 按照权重，从大到小排序
        return sentence_and_weight

    def search_relate_content_TFIDF_word2vec_hasMostSeg(self, seg_list, tfidf_threshold=0.5, w2v_threshold=0.7, w2v_sub_threshold=0.85): #对属性语句文本中已存在和缺失的进行wrod2vec相似度找词，最后排序时先按包含词的数目排序
        words = self.words
        all_fit_wrods = []  # 属性句子中所有要抽取相加的词，包括与问句完全匹配的分词和word2vec匹配最高的词
        all_fit_segs = []  # words中包含的seg
        for seg in seg_list:
            if seg in words:  # 语料库中包含问题分词
                all_fit_wrods.append([seg, 1, words.index(seg)])
                all_fit_segs.append([seg, words.index(seg)])
                max_fit_word = ['', w2v_sub_threshold, 0]  # 最匹配的词，[0]存词语，[1]存相似度, [2]存分词在语料词典中的位置
                for index, word in enumerate(words):
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
        weight =self.weight  # 将tf-idf矩阵抽取出来，元素a[i][j]表示j词在i类文本中的tf-idf权重
        sentence_and_weight = []
        for i in range(len(weight)):  # 打印每类文本的tf-idf词语权重，第一个for遍历所有文本，第二个for便利某一类文本下的词语权重
            sentence_weight = 0.0
            seg_exist_num = 0
            for j in all_fit_wrods:  # 计算TFIDF权重
                sentence_weight += weight[i][j[2]] * j[1]
            if sentence_weight > tfidf_threshold:
                for seg_info in all_fit_segs:
                    if weight[i][seg_info[1]] > 0:
                        seg_exist_num += 1
                sentence_and_weight.append((i, seg_exist_num, sentence_weight))  # 0：句子索引，1：句子中包含的问句分词数，2：句子的TFIDF权重
        sentence_and_weight.sort(key=lambda x: x[1] or x[2], reverse=True)  # 排序：先按句子包含的分词数，再按照权重，从大到小排序
        return sentence_and_weight