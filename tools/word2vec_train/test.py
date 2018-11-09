#coding=utf-8
#python2
import gensim
model_path = 'test.vector.bin'
model = gensim.models.KeyedVectors.load_word2vec_format(model_path, binary=True)
print model[u"工行"]
for data in model.wv.most_similar(positive=[u'工行'],topn=5):
    print data[0]
print model.n_similarity([u'工行'], [u'工商银行'])
print model.n_similarity([u'工行'], [u'交行'])
print model.similarity(u'工行',u'建行')