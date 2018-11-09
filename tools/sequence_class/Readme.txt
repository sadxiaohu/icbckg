1、关于各文件的说明：
   sequence_class.py：分类训练的主程序；
   original_data:训练所用到的原始数据，其中positive_sentence为正例即流程性表达，negative_sentence为负例即非流程性表述，stopwords里为常用停用词；
   intermediate_data:训练时处理的中间数据，未进行训练时为空；
   saved_model；该文件夹用于保存训练结果，包括1）word2id：分词到id的映射；2）训练所得模型对应的参数；3）训练所得模型在测试集上的结果。未进行训练时为空;
2、运行sequence_class脚本参数的说明：
   运行命令为：python sequence_class   --positive_data=**（训练所用正例的文件名，默认为positive_sentence.txt） --negative_data=**（训练所用负例的文件名，默认为negative_sentence.txt）--learning==**（训练所用的学习算法，默认为logistic，其他可选为svm,mlp）
3、注意事项
   1）脚本程序所用语言为python2；
   2）脚本所需第三方安装包有sklearn,jieba等；
   3）每进行一次训练时，需将intermediate_data文件夹内容清空