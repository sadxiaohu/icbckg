# -*- coding: utf-8 -*-
#python2
import logging
import os.path
import sys
import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import jieba
import time
# 将词列表合成字符串，词与词之间用空格隔开
def conv_l_to_s(l):
    s = ''
    for word in l:
        s += word + ' '
    return s[:-1]
# 数据预处理，去掉数据中的停用词，之后用jieba对每行数据进行分词，将分号的词用空格隔开保存到file_new中
def pre_process(file,file_new):
    training_dir = 'training_data/'
    inter_dir = 'intermediate_data/'
    stopwords = set()
    with open(training_dir+'stopwords.txt') as f:
        for _line in f:
            line = _line.strip().split(' ')
            for word in line:
                stopwords.add(word)
    new = open(inter_dir+file_new, 'ab')
    with open(training_dir+file) as f:
        for line_ in f:
            for stopword in stopwords:
                line_ = line_.replace(stopword,'')
            line = []
            for word in jieba.lcut(line_.strip()):
                w = word.encode('utf-8')
                line.append(w)
            new.write(conv_l_to_s(line)+'\n')

if __name__ == '__main__':
    t1 = time.time()
    file = 'banknews.txt'
    file_new = 'corpus.txt'
    pre_process(file,file_new)
    i_file = 'intermediate_data/' + file_new
    m_file = 'test.model'
    v_file = 'test.vector.bin'
    program = os.path.basename(sys.argv[0])  # 返回该程序的文件名
    for arg in sys.argv:
        print arg
    logger = logging.getLogger(program)
    FORMAT = '%(asctime)s: %(levelname)s: %(message)s'
    filename = 'run.log'
    level = logging.INFO
    logging.basicConfig(format=FORMAT,filename=filename,level=level)
    logger.info("running %s" % ' '.join(sys.argv))
    model = Word2Vec(LineSentence(i_file), size=200, window=5, min_count=5,  # size表示训练词向量的维度，min_count表示词频小于该值的词不参与训练，
            workers=multiprocessing.cpu_count())  # 训练所用线程个数
    model.save(m_file)
    model.wv.save_word2vec_format(v_file, binary=True)
    t2 = time.time()
    print "this procedure costs {} seconds".format(t2-t1)