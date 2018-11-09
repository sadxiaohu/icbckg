# coding:utf-8
import sys
import logging
import jieba
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import json
import gensim
import codecs

server_AnswerSelection_address = 'http://10.1.1.28:20002'

resource_path = sys.path[0] + '/resource'

# init set
logging_format = '%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s'
logging.basicConfig(filename=sys.path[0]+'/static/log/runlog.txt', level=logging.DEBUG, format=logging_format)

#KB directory
KB_path = resource_path+'/kg/new_nodes_links_7.json'

# load data
#属性抽取希望过滤的属性
not_extract_attributes = [str(line.strip()) for line in open(resource_path + "/attributeExtraction/not_extract_attributes", 'r').readlines()]
extract_attributes = [str(line.strip()) for line in open(resource_path + "/attributeExtraction/extract_attributes", 'r').readlines()]

#停止词
stop_words = [str(line.strip()) for line in open(resource_path + "/stopwords", 'r').readlines()]

# load model
print ("Loading model:word2vec ......")
w2v_model = gensim.models.KeyedVectors.load_word2vec_format(resource_path+'/word2vec/baike.vectors.bin', binary=True)

#待爬取的网址
spider_urls_path = sys.path[0] + '/spider/resource_urls.json'

#所有实体文本内容库
all_content = open(resource_path + "/indexBank/allContent", 'r').readline().strip()