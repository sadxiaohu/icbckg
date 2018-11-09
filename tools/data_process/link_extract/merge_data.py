# -*- coding: UTF-8 -*-
import json
import os
import codecs
defaultpath = './json'
keyword_list = [u'开通流程',u'申办流程',u'办理流程',u'业务流程',u'开办流程',u'操作流程', u'开办条件',u'操作指南',u'操作步骤']
sequence_list = [[u'（一）',u'（二）',u'（三）',u'（四）', u'（五）', u'（六）',u'（七）',u'（八）',u'（九）',u'（十）',u'（十一）',u'（十二）'],
                [u'1.',u'2.',u'3.',u'4.',u'5.',u'6.',u'7.',u'8.',u'9.',u'10.',u'11.',u'12.'],
                [u'1、',u'2、',u'3、',u'4、',u'5、',u'6、',u'7、',u'8、',u'9、',u'10、',u'11、',u'12、'],
                [u'(1)',u'(2)',u'(3)',u'(4)',u'(5)',u'(6)',u'(7)',u'(8)',u'(9)',u'(10)',u'(11)',u'(12)'],
                [u'一、',u'二、',u'三、',u'四、',u'五、',u'六、',u'七、',u'八、',u'九、',u'十、',u'十一、',u'十二、'],
                [u'（1）',u'（2）',u'（3）',u'（4）',u'（5）',u'（6）',u'（7）',u'（8）',u'（9）',u'（10）',u'（11）',u'（12）'],
                [u'1．',u'2．',u'3．',u'4．',u'5．',u'6．',u'7．',u'8．',u'9．',u'10．',u'11．',u'12．']]
attr_dict = {}
seq_sen_list = []
#提取流程性表达语句
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

#合并数据集
# id = 247001
# nodes = []
# with codecs.open('./'+'new_nodes_links.json','r',encoding='utf-8') as foo:
#     nodelist = json.load(foo)['nodes']
#     for node in nodelist:
#         nodes.append(node)
# for filename in os.listdir(defaultpath):
#     name = filename.split('_')[1].split('.')[0].encode('utf-8')
#     with codecs.open(defaultpath+'/'+filename,'r',encoding='utf-8') as foo:
#         node = json.load(foo)
#         node['name'] = name.decode('utf-8').encode('utf-8')
#         node['id'] = id
#         if 'taglist' in node:
#             try:
#               node['category'] = node['taglist'][1]
#             except:
#               print node['name']
#         nodes.append(node)
#         id += 1
# json_data = json.dumps({"nodes":nodes})
# with codecs.open('new_nodes.json','w',encoding='utf-8') as foo:
#     foo.write(json_data)
#统计属性次数
# with codecs.open('new_nodes.json','r',encoding='utf-8') as foo:
#     nodes = json.load(foo)['nodes']
#     for node in nodes:
#         for key in node:
#             if key not in attr_dict:
#                 attr_dict[key] = 1
#             else:
#                 attr_dict[key] += 1
# attr_tuple = sorted(attr_dict.items(),key=lambda x:x[1],reverse=True)
# with codecs.open('attr_sequence.txt','a',encoding='utf-8') as foo:
#     for attr in attr_tuple:
#         foo.write(attr[0]+' : ' + '  ' + str(attr[1])+'\n')
#提取流程性陈述句
with codecs.open('new_nodes.json','r',encoding='utf-8') as foo:
    nodes = json.load(foo)['nodes']
    for node in nodes:
        for key in node:
            if key in keyword_list:
                content = node[key]  # .decode('utf-8',errors = 'ignore')
                result = sequence_extract(content)
                if len(result) > 0:
                    seq_sen_list.extend(result)

seq_sen_list = set(seq_sen_list)
print 'positive examples no. :',len(seq_sen_list)
with codecs.open('./data/positive.txt','a',encoding='utf-8') as foo:
    for seq in seq_sen_list:
        foo.write(seq+'\n')
#提取非流程性陈述句
otherword_list = [u'业务简介',u'注意事项',u'常见问题',u'功能特点',u'名词解释']
non_sen_list = []
non_sen_no = 1
for node in nodes:
    for key in node:
        if key in otherword_list:
            content = node[key]
            if len(content) >= 20:
                result = content.split(u'。')
                for sentence in result:
                    non_sen_list.append(sentence)
non_sen_list = set(non_sen_list)
with codecs.open('./data/negative.txt','a',encoding='utf-8') as foo:
    for seq in non_sen_list:
        seq = seq.strip()
        if non_sen_no <= 2100 :
             for sequence in sequence_list:
                 for word in sequence:
                     if word in seq:
                         seq = seq.replace(word,'')
             seq = seq.strip()
             if len(seq) >= 10 :
                 foo.write(seq+'\n')
                 non_sen_no += 1
print 'negative examples no. :',non_sen_no-1