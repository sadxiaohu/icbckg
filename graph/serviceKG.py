# coding=utf-8
import owlNeo4j
import serviceQA
import serviceWord2vec
import re
import jieba
import json
import icbckg.config as config
import logging
import questionClassification.sequence_class as sequence_class
kb = json.load(open(config.KB_path))['nodes']
links = json.load(open(config.KB_path))['links']

namelist = []
catelist = []
for node in kb:
    jieba.add_word(node['name'])  # 将语料库中的专有名字加入结巴词库
    namelist.append(node['name'])
    taglist = node['taglist'].split(',')
    for tag in taglist:
        jieba.add_word(tag)  # 将语料库中的专有的tag加入结巴词库
        catelist.append(tag)
for word in [u'利率',u'产品利率',u'存款利率',u'贷款利率',u'高于',u'低于',u'等于']:
    jieba.add_word(word)
num_dict = {u'第一': 0, u'第二': 1, u'第三': 2, u'第四': 3, u'第五': 4,
           u'第六': 5, u'第七': 6, u'第八': 7, u'第九': 8, u'第十': 9,
           u'第十一': 10, u'第十二': 11, u'第十三': 12, u'第十四': 13, u'第十五': 14,u'最高':0,u'最大':0,
            u'最低':0,u'最小':0,u'第二小':1,u'第三小': 2, u'第四小': 3, u'第五小': 4,
            u'第二低': 1, u'第三低': 2, u'第四低': 3, u'第五低': 4}
queryword_list = [u'哪个',u'哪一个',u'怎么',u'怎么办',u'谁',u'如何',u'哪些',u'多少',u'为什么',u'怎么样',u'哪里']
num_list = {u'1.',u'2.',u'3.',u'4.',u'5,',u'6,',u'7.',u'8.',u'9.',u'10.'}
for key in num_dict:
    jieba.add_word(key)
def knowledge_graph(question, neoid=None, autopick=False):#autopick表示是否开启自动选择
    # 如果已经选好了实体，直接返回实体检索结果
    if neoid is not None:
        return decorate(neoid, style='BASIC')
    question.strip()
    if any(num in question for num in num_list):
        switch = True
    else:
        switch = False
    for queryword in queryword_list:
        if queryword in question:
            question = question.replace(queryword,'')
    # 比较型问题
    pattern = r'^.+比.+(高|低).*$'
    if re.search(pattern,question.decode('utf-8').encode('utf-8')) != None:
        seg_list = serviceQA.segment(question)
        seg_list_complete = []
        for seg in seg_list:
            seg_list_complete.append(seg.word)
        relatedwords = [u'利率',u'产品利率',u'存款利率',u'贷款利率']
        word_1,word_2 = '',''
        for seg in seg_list_complete:
            if seg in namelist and seg_list_complete.index(seg) < seg_list_complete.index('比'):
                word_1 = seg
                continue
            if seg in namelist and seg_list_complete.index(seg) > seg_list_complete.index('比'):
                word_2 = seg
                break
        if len(owlNeo4j.get_entity_list_by_name(word_1)) > 0 and len(owlNeo4j.get_entity_list_by_name(word_2)) > 0:
            word_1 = owlNeo4j.get_entity_list_by_name(word_1)[0]
            word_2 = owlNeo4j.get_entity_list_by_name(word_2)[0]
            for word in relatedwords:
                if word in word_1  and  word in word_2:
                    return decorate(data = '1',style='COM',question = question)
    #按类别查询
    if 'c::' in question:
        category = question.split('c::')[1].strip()
        for node in kb:
            for tag in node['taglist'].split(','):
                score = owlNeo4j.entity_similarity(category,tag)
                if category == tag or score >= 0.5:
                   return decorate('2','CAT',question = question)
    #按关系查询
    if 'r::' in question:
        relation = question.split('r::')[1].strip()
        if relation.find('<') == -1 :
            for link in links:
                score = serviceWord2vec.get_similarity(list(jieba.cut(relation)), list(jieba.cut(link['name'])))
                if relation == link['name'] or score >= 0.6:
                    return decorate('3','LIN',question = question)
        else:
            return decorate('3','LIN',question = question)
    #归纳型问题
    seg_list = serviceQA.segment(question)
    #seg_list_complete = []
    for seg in seg_list:
        #seg_list_complete.append(seg.word)
        if seg.word in [u'利率',u'产品利率',u'存款利率',u'贷款利率']:
            for seg in seg_list:
                if seg.word in catelist:
                    for seg in seg_list:
                      if seg.word in num_dict:
                        return decorate('4','IND',question = question)
    #检索型问题
    for seg in seg_list:
        if seg.word in [u'利率',u'产品利率',u'存款利率',u'贷款利率']:
            for seg in seg_list:
                if seg.word in catelist:
                    for seg in seg_list:
                      if seg.word in [u'高于',u'低于',u'等于']:
                          for seg in seg_list:
                               if seg.flag == 'm':
                                   return decorate('5','RET',question = question)
    #流程性问题
    pre = sequence_class.question_class(question)
    if pre == 1:
          result = serviceQA.autoseq(question)
          if result != 0 :
              return decorate(result,style='QA')
    # 进行中文问答
    qa_result = serviceQA.chinese_qa(question,switch)
    logging.info("qa_result:"+json.dumps(qa_result, encoding='utf-8', ensure_ascii=False))
    if (qa_result is None):
        return None
    # 如果是实体检索
    if 'question' in qa_result:  # 如果存在（实体，关系）对的相似问题
        return decorate(qa_result['question'],style='QUE')
    if len(qa_result['path']) == 0:  # 如果path为空，即不存在关系
        if autopick or (len(qa_result['ents']) == 1):  # 如果开启自动选择或只存在一个实体
            return decorate(qa_result['ents'][0]['neoId'], style='BASIC')
        else:  # 如果存在多个实体且没开启自动选择
            return decorate(qa_result['ents'], style='SNET')
    else:
        if qa_result['ents'][0]['neoId'] == None:
            return decorate(qa_result, style='TS')  # 全文信息检索
        return decorate(qa_result, style='QA')  # 从属性里找答案，或者有匹配的（实体，属性，实体）


# 针对不同的需求配置不同的结果json文件
def decorate(data, style,question = None):
    if style == 'BASIC':  # 普通实体查询配置，data为实体的neoId
        result = bloom(data)
        result['answer'] = "为你找到关于 " + result['nodes'][0]['name'] + " 的信息"
        return result
    if style == 'COM': # 比较型问题
        result = bloom(data,question = question)
        return result
    if style == 'CAT': # 按类别查询
        result = bloom(data,question = question)
        return result
    if style == 'LIN': # 按关系查询
        result = bloom(data,question = question)
        return result
    if style == 'IND': # 归纳型问题
        result = bloom(data,question = question)
        return result
    if style == 'RET': # 检索型问题
        result = bloom(data,question = question)
        return result
    if style == 'SNET':  # 同名实体列表配置，data为同名实体列表
        result = {'entities': data, 'answer': '请在参考实体列表中选择'}
        return result
    if style == 'QA':  # 问答配置，data为问答结果
        result = bloom(data['ents'][0]['neoId'], path=data['path'])
        result['answer'] = answer_generate(data['path'])
        return result
    if style == 'QUE':  # 多问题模糊匹配
        result = {'questions': data,'answer': '请在参考问题列表中选择'}
        return result
    if style == 'TS':  # 全文信息检索
        result = bloom('6', path=data['path'][0])
        result['answer'] = answer_generate(data['path'])
        return result
    return None


# 生成图谱
def bloom(root, path=None,question = None):
    if root == '1': # root为'1'代表该类问题为比较性问题(注意是字符串的'1'，不是数字1，root可是能数字1，表示neoId=1的节点)
        result = serviceQA.autocom(question)
        if result != 0:
            return result
    if root == '2': # root为'2'代表按类别查询
        result = serviceQA.autocate(question)
        if result != 0:
            return result
    if root == '3': # root为'3'代表按关系查询
        return serviceQA.autolink(question)
    if root == '4': # root为'4'代表归纳类问题
        result = serviceQA.autoinduce(question)
        if result != 0:
            return result
    if root == '5': # root为5代表检索型问题
        result = serviceQA.autoret(question)
        if result != 0:
            return result
    if root == '6':  # root为6代表全文信息检索型问题
        result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}
        source = path[0]
        relation = path[1]
        target = path[2]
        new_node1 = {'id': 0, 'name': source['name'], 'category': source['category'], 'neoId': None, 'content': source['问题'], 'value': 0}
        # new_node2 = {'id': 1, 'name': target['name'], 'category': target['category'], 'neoId': None, 'content': target['ans_from_desc'], 'value': 1}
        # new_edge1 = {'id': 0, 'name': relation, 'level': 1, 'source': 0, 'target': 1}
        result['nodes'].append(new_node1)
        # result['nodes'].append(new_node2)
        # result['links'].append(new_edge1)
        return result
    graph_result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}

    if root is None:
        return graph_result
    pointer = 0  # 待被查询的节点队列指针，指向graph_result中结点
    max_level = 2
    # 添加根节点
    entity_info = owlNeo4j.get_entity_info_by_id(root)
    new_node = {'id': 0, 'name': entity_info['name'], 'category': entity_info['category'], 'neoId': root, 'value': 0}
    graph_result['nodes'].append(new_node)
    # 广度递归后续节点，如果层数没有达到上限，并且还存在待被查询的节点，并且目前节点数小于100就继续
    while (len(graph_result['nodes']) > pointer) and (len(graph_result['nodes']) < 100) and (graph_result['nodes'][pointer]['value'] < max_level):
        max_related_entities_num = 9 # if pointer != 0 else None
        related_entities = owlNeo4j.get_twoway_related_entities_by_id(graph_result['nodes'][pointer]['neoId'], max_num=max_related_entities_num)
        for related_entity in related_entities:
            relation = related_entity['name']
            category = related_entity['target_category']
            name = related_entity['target_name']
            neoid = related_entity['target_neoId']
            # 如果这个节点之前不存在，加入新节点
            id_target = None
            for node_exist in graph_result['nodes']:
                if node_exist['neoId'] == neoid:
                    id_target = node_exist['id']
                    break
            if id_target is None: #如果是新节点
                new_node = {'id': len(graph_result['nodes']), 'name': name, 'category': category, 'neoId': neoid,
                            'value': graph_result['nodes'][pointer]['value'] + 1}#从0开始重新取id
                graph_result['nodes'].append(new_node)
                id_target = new_node['id']
            # 如果目前与当前实体还没有关系，加入新关系
            if not any(((link_exist['source'] == pointer and link_exist['target'] == id_target) or
                        (link_exist['source'] == id_target and link_exist['target'] == pointer))
                       for link_exist in graph_result['links']):
                new_edge = {'id': len(graph_result['links']), 'name': relation, 'level': graph_result['nodes'][pointer]['value'] + 1}
                if related_entity['positive']:  # positive为True表示正向关系，positive为False表示反向关系
                    new_edge['source'] = pointer
                    new_edge['target'] = id_target
                else:
                    new_edge['source'] = id_target
                    new_edge['target'] = pointer
                graph_result['links'].append(new_edge)
        pointer += 1
    graph_result['answerpath'].append(0)
    # 加入答案路径
    if path is not None:
        graph_result['answerlist'] = path
        for index, triple in enumerate(path):  # index表示索引，triple表示三元组
            i = None
            j = None
            for index0, e0 in enumerate(graph_result['nodes']):
                if triple[0]['neoId'] == e0['neoId']:#triple[0]['neoId']表示source结点
                    i = index0
                if triple[2]['neoId'] == e0['neoId']:#triple[2]['neoId']表示target结点
                    j = index0
            if i is None:
                i = len(graph_result['nodes'])
                graph_result['nodes'].append({'id': i, 'name': triple[0]['name'], 'neoId': triple[0]['neoId'], 'value': 1,
                                              'category': triple[0]['category']})
            if j is None:
                j = len(graph_result['nodes'])
                graph_result['nodes'].append({'id': j, 'name': triple[2]['name'], 'neoId': triple[2]['neoId'], 'value': 1,
                                              'category': triple[2]['category']})
            graph_result['links'].append({'id': len(graph_result['links']), 'source': i, 'target': j, 'name': triple[1]})
            if i not in graph_result['answerpath']:
                graph_result['answerpath'].append(i)
            if j not in graph_result['answerpath']:
                graph_result['answerpath'].append(j)
    return graph_result


# 从结构化数据生成自然语言回答
def answer_generate(path):
    if 'ans_from_desc' in path[-1][-1]:  # 如果答案来自于描述文本 answer from description
        result = path[-1][-1]['ans_from_desc']
    else:
        result = ""
        for i in range(len(path)):
            if (i < len(path)-1) and (path[i][0]['name'] == path[i+1][0]['name']) and (path[i][1] == path[i+1][1]):  # 枚举类型答案实体。同一个源结点，关系相同
                enumerate_answer_list = [step[2]['title'] for step in path[i:]]
                result += path[i][0]['name'] + '的' + path[i][1] + '有' + str(len(enumerate_answer_list)) + '个：'
                result += "、".join(enumerate_answer_list)
                break
            else:
                # if i > 0:
                #     result += "，"
                if path[i][1] != "description":
                    result += path[i][0]['name']+'的'+path[i][1]+'是'+path[i][2]['title']
                else:
                    result += path[i][0]['name']+'是' + path[i][2]['title']

    return result
