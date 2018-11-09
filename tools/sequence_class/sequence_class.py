# -*- coding: UTF-8 -*-
#python2
import random
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.neural_network import MLPClassifier
import pickle as cPickle
import jieba
import argparse
import time

def filter_w():
    data_dir = 'intermediate_data/'
    word_dict = {}
    with open(data_dir+'positive.txt') as f:  #  统计已分好了的词在正样本中的次数
        for _line in f:                      #_ line表示文本中的行，即文本是按行迭代的
            for word in _line.strip().split(' '):
                if word not in word_dict:
                    word_dict[word]	= [0, 0]
                word_dict[word][0] += 1

    with open(data_dir+'negative.txt') as f:
        for _line in f:
            for word in _line.strip().split(' '):
                if word not in word_dict:
                    word_dict[word]	= [0, 0]
                word_dict[word][1] += 1
    w_dict = {}
    for key in word_dict:
        w_dict[key] = [word_dict[key][0] - word_dict[key][1], word_dict[key][0] + word_dict[key][1]]  # word_dict[key][0] - word_dict[key][1]指正样本出现的词减去负样本中该词的次数，次数越大表明正样本的出现与该词有很大关系
    sorted_w = sorted(w_dict.items(), key=lambda x:x[1], reverse=True)   # 按第一项（word_dict[key][0] - word_dict[key][1]）的大小降序排列
    with open(data_dir+'filter.txt', 'ab') as f:
        for item in sorted_w:
            if item[1][0] == item[1][1]:  # 该等式含义是：仅在正样本中出现的分词
                f.write(item[0]+'	'+str(item[1][0])+'	'+str(item[1][1])+'\n')

def conv_l_to_s(l):  # 在可迭代对象的各个元素之间加空格
    s = ''
    for word in l:
        s += word + ' '
    return s[:-1]

def stopwords(file, file_new):  # 去除停用词
    data_dir = 'original_data/'
    inter_dir = 'intermediate_data/'
    stopwords = set()  # 定义一个空集合
    with open(data_dir+'stopwords.txt') as f:  # 将停用词库中的文本数据转换成便于处理的集合
        for _line in f:
            line = _line.strip().split(' ')
            for word in line:
                stopwords.add(word)  # 向集合中添加元素
    new = open(inter_dir+file_new, 'ab')
    with open(data_dir+file) as f:
        for line_ in f:
            line = []
            for word in jieba.lcut(line_.strip()): # jieba.lcut()作用为分词，返回结果为列表
                w = word.encode('utf-8')  # 可以省略此行
                if w not in stopwords:
                    line.append(w)
            new.write(conv_l_to_s(line)+'\n')


def dataprocess():
    data_dir = 'intermediate_data/'
    normal_text = []
    sens_text = []
    with open(data_dir+'negative.txt') as f:
        for line in f:
            normal_text.append((line, 0))
    with open(data_dir+'positive.txt') as f:
        for line in f:
            sens_text.append((line, 1))
    random.shuffle(normal_text)  # shuffle将一个数列随机排列
    random.shuffle(sens_text)
    train_text = normal_text[200:]
    train_text.extend(sens_text[200:])
    test_text = normal_text[:200]      # 分词结果的前500行信息作为测试集
    test_text.extend(sens_text[:200])
    random.shuffle(train_text)
    random.shuffle(test_text)
    all_data = open(data_dir+'all_text.txt', 'ab')
    train_data = open(data_dir+'train_text.txt', 'ab')
    test_data = open(data_dir+'test_text.txt', 'ab')
    all_label = open(data_dir+'all_label.txt', 'ab')
    train_label = open(data_dir+'train_label.txt', 'ab')
    test_label = open(data_dir+'test_label.txt', 'ab')
    for i in range(len(train_text)):
        all_data.write(train_text[i][0])
        all_label.write(str(train_text[i][1])+'\n')
        train_data.write(train_text[i][0])
        train_label.write(str(train_text[i][1])+'\n')
    for i in range(len(test_text)):
        all_data.write(test_text[i][0])
        all_label.write(str(test_text[i][1])+'\n')
        test_data.write(test_text[i][0])
        test_label.write(str(test_text[i][1])+'\n')
    # print 'OK'

def normalize(M, max_val):  # 规则化。在二维数组M中，大于max_val的值赋为1，小于max_val的值则除以max_val
    M[M>max_val] = max_val
    return M/max_val

class sent_class():

    def __init__(self, data_dir, save_dir, max_iter=5000):

        self.data_dir = data_dir
        self.save_dir = save_dir
        self.max_iter = max_iter
        self.word2id = {}
        self.id2word = {}

    def save(self, model, name):
        with open(self.save_dir+'%s.pkl'%name, 'wb') as fid:
            cPickle.dump(model, fid)

    def load(self, name):
        with open(self.save_dir+'%s.pkl'%name, 'rb') as fid:
            model = cPickle.load(fid)
        return model

    def load_txt(self, file_name):
        text = []
        with open(self.data_dir+file_name) as f:
            for line in f:
                text.append([x for x in line.strip().split(' ')])
        return text

    def load_label(self, file_name):
        label = []
        with open(self.data_dir+file_name) as f:
            for line in f:
                label.append(int(line.strip()))
        return np.asarray(label, dtype=np.float32)  # asarray作用是将列表，元组等对象转化成矩阵（array），dtype控制输出元素的格式

    def ge_word_dict(self, word_list):
        word_dict = {}
        for line in word_list:
            for word in line:    #1-gram
            	if word not in word_dict:
            		word_dict[word] = 1
            	else:
            		word_dict[word] += 1

            for index in range(len(line) - 1):    #2-gram
            	if line[index]+line[index+1] not in word_dict:
            		word_dict[line[index]+line[index+1]] = 1
            	else:
            		word_dict[line[index]+line[index+1]] += 1

            # for index in range(len(line) - 2):    #3-gram
            #     if line[index]+line[index+1]+line[index+2] not in word_dict:
            #         word_dict[line[index]+line[index+1]+line[index+2]] = 1
            #     else:
            #         word_dict[line[index]+line[index+1]+line[index+2]] += 1
        sorted_list = sorted(word_dict.items(), key=lambda x:x[1], reverse=True)
        with open(self.data_dir+'word_num.txt', 'ab') as f:
            for item in sorted_list:
                f.write(item[0]+'	'+str(item[1])+'\n')

    def init_word_id(self, low, high,name):
        index = 0
        filter_words = set()
        with open(self.data_dir+'filter.txt') as f:
            for line in f:
                filter_words.add(line.strip().split('	')[0])#去掉词语对应的数字仅保留词语
        with open(self.data_dir+'word_num.txt') as f:
            for _line in f:
                line = _line.strip().split('	')
                if len(line)<2: #小于两项的不进行处理（不过每一行都是两项吧）
                    continue
                word = line[0]  #词
                freq = int(line[1]) #词频
                if freq>=low and freq<=high  and word!='　':
                    self.word2id[word] = index #index含义是索引，即每一个分词在word2id中对应的位置
                    #print index
                    self.id2word[index] = word
                    #print index,word
                    index += 1
        with open(self.save_dir+name+'_word2id.pkl', 'wb') as fid:
            cPickle.dump(self.word2id, fid)
        # print len(self.word2id)
        # print len(self.id2word)

    def get_text_vec(self, text_list):
        dim = len(self.word2id)
        #print dim
        text_vec = []
        for line in text_list:
            vec = np.zeros(dim, dtype=np.float16)  #返回一个指定形状用零填充的数组
            for word in line:   # 1-gram
            	if word in self.word2id:
            		vec[self.word2id[word]] = vec[self.word2id[word]] + 1
            #text_vec.append(vec)
            for index in range(len(line) - 1):    #2-gram
                if line[index]+line[index+1]  in self.word2id:
                    vec[self.word2id[line[index]+line[index+1]]] = vec[self.word2id[line[index]+line[index+1]]] + 1
            #text_vec.append(vec)
            # for index in range(len(line) - 2):  # 3-gram
            #     if line[index] + line[index + 1] + line[index + 2] in self.word2id:
            #         vec[self.word2id[line[index] + line[index + 1]  + line[index + 2]]] = vec[self.word2id[line[index] + line[index + 1] + line[index + 2]]] + 1
            text_vec.append(vec)
        #print text_vec
        return np.asarray(text_vec, dtype=np.float32)

    def train(self, X, y, save_name, model_type='logistic'):
        if model_type =='logistic':
            model = LogisticRegression(max_iter=self.max_iter) #LOGISTIC max_iter表示最大迭代次数
        elif model_type =='svm':
            model = LinearSVC(max_iter=self.max_iter) #SVM
        elif model_type =='mlp':
            model = MLPClassifier(max_iter=self.max_iter) #MLP
        model.fit(X, y)
        self.save(model, save_name)

    def pred(self, model, X):
        return model.predict(X)

    def evaluation(self, pred, label):
        count = 0
        sen_to_sen = 0
        sen_to_nor = 0
        nor_to_nor = 0
        nor_to_sen = 0
        lens = len(pred)
        for i in range(lens):
            if pred[i]==label[i]:
                count += 1
            if pred[i] == 1 and  label[i] == 1:
                sen_to_sen += 1
            if pred[i] == 1 and label[i] == 0:
                nor_to_sen += 1
            if pred[i] == 0 and label[i] == 1:
                sen_to_nor += 1
            if pred[i] == 0 and label[i] == 0:
                nor_to_nor += 1
        print u'预测结果：非流程性语句预测为非流程性语句有%d条'%nor_to_nor
        print u'预测结果：流程性语句预测为流程性语句有%d条'%sen_to_sen
        print u'预测结果：非流程性语句预测为流程性语句有%d条'%nor_to_sen
        print u'预测结果：流程性语句预测为非流程性语句有%d条'%sen_to_nor
        return float(count)/lens

    def get_key_words(self, coefs):
        coef = coefs.reshape(-1)  # reshape()方法，将矩阵重新塑形。当参数为-1时，矩阵中所有行合并成一行，成为单行矩阵。reshape(n1,n2)表示将矩阵重新塑造成n1行n2列的新矩阵
        topk = np.argsort(coef)[::-1]# np.argsort 对参数进行升序排序，返回的是参数所对应的index
        with open(self.save_dir+'key_words.txt', 'ab') as f:
            for i in topk:
                f.write(self.id2word[i]+'	'+str(coef[i])+'\n')



if __name__=='__main__':
    t1 = time.time()
    parser = argparse.ArgumentParser(description='parameters for training in logistic,svm or mlp')
    parser.add_argument('--positive_data',default='positive_sentence.txt',help='the name of file containing positive examples.')
    parser.add_argument('--negative_data',default='negative_sentence.txt',help='the name of file containing negative examples.')
    parser.add_argument('--learning_method',default='logistic',help='the training method.')
    args = parser.parse_args()
    positive_data = args.positive_data
    negative_data = args.negative_data
    learning_method = args.learning_method
    stopwords(positive_data, 'positive.txt')  # 异常信息去除停用词得到postive.txt（已用jieba分词）
    stopwords(negative_data, 'negative.txt')  # 正常信息去除停用词得到negative.txt（已用jieba分词）
    filter_w() #得到filter.txt，每一项为在正样本中存在而在负样本中不存在的分词，以及在正样本中出现的次数
    dataprocess()#得到all_text,all_label,train_text,train_label,test_text,test_label（按分完词的文本行）
    model = sent_class('intermediate_data/', 'saved_model/')#定义了一个sent_class类对象
    all_text = model.load_txt('all_text.txt')#得到一个二维列表all_text，列表的一项对应all_text的一行
    model.ge_word_dict(all_text) #获得词频，存储在word_num里面，形式是：词 出现次数。测试用的是三元组1-gram,2-gram
    model.init_word_id(2, 500,learning_method) #5和1000表示所处理的词频上下界。得到word2id和id2word两个字典。其中word2id的每一项表示1-gram的每个分词以及所在的位置(index)
    # max_val = 4.0
    train_text = model.load_txt('train_text.txt')#得到一个二维列表train_text，列表的一项对应train_text的一行
    # train_text_vec = normalize(model.get_text_vec(train_text), max_val)#model.get_text_vec(train_text)得到train_text的二维特征向量
    train_text_vec = model.get_text_vec(train_text)
    train_label = model.load_label('train_label.txt')#得到一个一维数组
    model.train(train_text_vec, train_label, learning_method, model_type=learning_method)#训练模型，并将训练的结果保存到'logistic'
    test_text = model.load_txt('test_text.txt')
    # test_text_vec = normalize(model.get_text_vec(test_text), max_val)#model.get_text_vec(test_text)返回的是训练集的特征向量
    test_text_vec = model.get_text_vec(test_text)
    test_label = model.load_label('test_label.txt')
    class_model = model.load(learning_method)
    pred = model.pred(class_model, test_text_vec) # 对测试集进行预测并判断结果
    accuracy = model.evaluation(pred, test_label)
    with open('saved_model/'+learning_method+'_test_results.txt', 'ab') as f:
        f.write('model: %s  accuracy: %.3f\n'%(learning_method,accuracy))
    print 'test accuracy: %.3f'%accuracy
    # coefs = class_model.coef_#class_model这个模型中的系数，返回结果是一个矩阵（ndarray）
    # model.get_key_words(coefs)
    print 'OK'
    t2 = time.time()
    print 'This procedure costs %f seconds.'%(t2-t1)

