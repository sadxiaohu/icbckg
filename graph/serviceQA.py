# coding=utf-8
import jieba.posseg as posseg
import jieba
import owlNeo4j
import serviceWord2vec
import attributeMatch
import attributeMatch_seq
import logging
import icbckg.config as config
import sys
import serviceKG
import json
import textSearch
reload(sys)
sys.setdefaultencoding('utf8')
keyword_list = [u'开通流程',u'申办流程',u'办理流程',u'业务流程',u'开办流程',u'操作流程',u'开办条件',u'使用窍门',u'特色优势',u'操作指南',u'操作步骤','“',',']
sequence_list = [[u'（一）',u'（二）',u'（三）',u'（四）', u'（五）', u'（六）',u'（七）',u'（八）',u'（九）',u'（十）',u'（十一）',u'（十二）'],
                [u'1.',u'2.',u'3.',u'4.',u'5.',u'6.',u'7.',u'8.',u'9.',u'10.',u'11.',u'12.'],
                [u'1、',u'2、',u'3、',u'4、',u'5、',u'6、',u'7、',u'8、',u'9、',u'10、',u'11、',u'12、'],
                [u'(1)',u'(2)',u'(3)',u'(4)',u'(5)',u'(6)',u'(7)',u'(8)',u'(9)',u'(10)',u'(11)',u'(12)'],
                [u'一、',u'二、',u'三、',u'四、',u'五、',u'六、',u'七、',u'八、',u'九、',u'十、',u'十一、',u'十二、'],
                [u'（1）',u'（2）',u'（3）',u'（4）',u'（5）',u'（6）',u'（7）',u'（8）',u'（9）',u'（10）',u'（11）',u'（12）'],
                [u'1．',u'2．',u'3．',u'4．',u'5．',u'6．',u'7．',u'8．',u'9．',u'10．',u'11．',u'12．']]
queryword_list = [u'哪个',u'哪一个',u'怎么',u'怎么办',u'谁',u'如何',u'哪些',u'多少',u'为什么',u'怎么样',u'哪里',u'是什么']
punctuation_list = [u'，',u'。',u'？',u'!',u'：',u'-',u'“',u'”',u',',u'.',u'?',u'!',u':',u'_',u'"']
another_name_dict = {u"网银":u"网上银行",u"工行":u"中国工商银行",u"ATM":u"自动取款机",u"自助机":u"自动柜员机",u"自动取款机":u"自动柜员机",u"取款机":u"自动柜员机",u"柜员机":u"自动柜员机",u"灵通卡":u"牡丹卡",u"e时代卡":u"e卡",u"理财金卡":u"工银理财金账户卡",u"网点":u"营业网点"}  # 别名表

def chinese_qa(question,switch):
    global out_question
    out_question = question
    if len(question) >= 3 and question.find('什么是') == 0:
        question = question.replace('什么是','').replace('？','')+'是什么'
    for name in another_name_dict:
        if name in question:
            question = question.replace(name, another_name_dict[name])
    logging.info('question:' + question)
    # 分词
    seg_list_complete = segment(question)
    seg_list = []
    seg_result = ""
    first_n_position = -1
    for index, word in enumerate(seg_list_complete):
        seg_list.append(word.word)
        seg_result += word.word + '/' + word.flag + ' '
        if word.flag in ['n','x','nr','ns','Ng','nt','nz']:  #找一个名词出现位置
            if first_n_position == -1:
                first_n_position = index
    logging.info('segment result: ' + seg_result)
    if first_n_position != -1 and first_n_position != 0:  #模板：第一个名词前的动词后移到该名词之后
        if seg_list_complete[first_n_position-1].flag == 'v':
            temp = seg_list[first_n_position-1]
            seg_list[first_n_position - 1] = seg_list[first_n_position]
            seg_list[first_n_position] = temp
    logging.info('segment list: '+json.dumps(seg_list, ensure_ascii=False))
    # 问答有穷自动机
    qa_result = automata(seg_list,switch,question)
    return qa_result


# 问答有穷自动机 QA
def automata(seg_list,switch,question):
    threshold = 0.6  # 向量相似度匹配的状态转移阈值
    threshold_2 = 0.2  # 关系相似度（编辑距离）的转移阈值
    threshold_3 = 0.4  # 文本答案选择匹配的状态转移阈值
    threshold_4 = 0.6  # 在只查找到实体的情况下，实体名长度占问题长度的比例转移阈值
    true_question = {}
    questionlist = []
    states = []
    caches = {}
    multi_question = question.split('？')
    if multi_question[-1] == '':
        multi_question = multi_question[:-1]
    if len(multi_question) > 1:
        return {'question': multi_question}
    if switch is False:
        count = 0
        label = 1
        for word in seg_list:
            new_states = []
            states.append({'header': None, 'tailer': None, 'available_words': [], 'path': [], 'score': 0})
            for state in states:
                state['available_words'].append(word)
                # 对于START状态
                if (state['header'] is None):
                    entity_name = "".join(state['available_words'])
                    same_name_entity_list = owlNeo4j.get_entity_list_by_name(entity_name)
                    for entity in same_name_entity_list:
                        new_states.append(
                            {'header': entity, 'tailer': None, 'available_words': [], 'path': [], 'score': 1})
                # 对于非START状态
                else:
                    if state['tailer'] is None:
                        source = {'name': state['header']['name'], 'category': state['header']['category'],
                                  'neoId': state['header']['neoId']}
                    else:
                        source = state['tailer']
                    if source['neoId'] is None:  # neoId is None 意味着路径走到了一个不可跳转的状态
                        continue
                    if source['neoId'] not in caches:  # 整理这个实体的关系与属性集，加入到缓存中等待使用
                        caches[source['neoId']] = []
                        relations = owlNeo4j.get_oneway_related_entities_by_id(source['neoId'])
                        for relation in relations:  # 添加关系
                            caches[source['neoId']].append(relation)
                        props = owlNeo4j.get_entity_info_by_id(source['neoId'])
                        for prop in props:  # 添加属性，如果已经有同名关系出现，则该属性不添加
                            if any(prop == relation['name'] for relation in caches[source['neoId']]):
                                continue
                            flag = 0
                            if prop in keyword_list:
                                content = props[prop]
                                for sequence in sequence_list:
                                    if sequence[0] in content:
                                        target_sequence = sequence
                                        flag = 1
                                        break
                            if flag == 1:
                                num = 0
                                id = 0
                                for i in range(len(target_sequence)):
                                    num += 1
                                    if target_sequence[i] not in content:
                                        num = num - 1
                                        break
                                for i in range(num):
                                    if i < num - 1:
                                        start = content.index(target_sequence[i])
                                        end = content.index(target_sequence[i + 1])
                                        # target_content = content[start:end] if (end-start) <= 10 else content[start:start+10]+'...'
                                        caches[source['neoId']].append(
                                            {'name': prop, 'target_category': '属性值', 'target_name': content[start:end],
                                             'target_neoId': 100000 + id})
                                        id += 1
                                    else:
                                        start = content.index(target_sequence[i])
                                        # target_content = content[start:] if len(content[start:]) <= 10 else content[start:start+10]+'...'
                                        caches[source['neoId']].append(
                                            {'name': prop, 'target_category': '属性值', 'target_name': content[start:],
                                             'target_neoId': 100000 + id})
                                        id += 1
                            else:
                                # target_content = str(props[prop]) if len(str(props[prop])) <= 10 else str(props[prop])[0:10]+'...'
                                caches[source['neoId']].append(
                                    {'name': prop, 'target_category': '属性值', 'target_name': props[prop],
                                     'target_neoId': None})
                    # 对于所有关系属性逐个进行相似度匹配, 大于阈值就进行状态转移
                    link2state_map = {}
                    for link in caches[source['neoId']]:
                        score = serviceWord2vec.get_similarity(state['available_words'], list(jieba.cut(link['name'])))
                        if state['available_words'] == list(jieba.cut(link['name'])):
                            score = 1.0
                        if score >= threshold:
                            if owlNeo4j.levenshtein(link['name'], ''.join(state['available_words'])) >= threshold_2 or (
                                    u'是什么' == ''.join(state['available_words'])):
                                value = state['header']['score'] * score
                                question = state['header']['name'] + '的' + link['name'] + '是什么'
                                if question not in true_question:
                                    true_question[question] = value
                                else:
                                    if value > true_question[question]:
                                        true_question[question] = value
            states += new_states
        if true_question is not None:
            true_question = list(sorted(true_question.items(), key=lambda x: x[1], reverse=True))
            for question in true_question:
                questionlist.append(str(label) + '.' + question[0])
                label += 1
    else:
        count = 1
        seg_list = seg_list[1:]
        for word in seg_list:
            logging.info("seg_list:" + '/'.join(seg_list))
            new_states = []
            states.append({'header': None, 'tailer': None, 'available_words': [], 'path': [], 'score': 0})
            for state in states:
                state['available_words'].append(word)
                # 对于START状态
                if (state['header'] is None):
                    entity_name = "".join(state['available_words'])
                    same_name_entity_list = owlNeo4j.get_entity_list_by_name(entity_name)
                    for entity in same_name_entity_list:
                        new_states.append(
                            {'header': entity, 'tailer': None, 'available_words': [], 'path': [], 'score': 1})
                # 对于非START状态
                else:
                    if state['tailer'] is None:
                        source = {'name': state['header']['name'], 'category': state['header']['category'],
                                  'neoId': state['header']['neoId']}
                    else:
                        source = state['tailer']
                    if source['neoId'] is None:  # neoId is None 意味着路径走到了一个不可跳转的状态
                        continue
                    if source['neoId'] not in caches:  # 整理这个实体的关系与属性集，加入到缓存中等待使用
                        caches[source['neoId']] = []
                        relations = owlNeo4j.get_oneway_related_entities_by_id(source['neoId'])
                        for relation in relations:  # 添加关系
                            caches[source['neoId']].append(relation)
                        props = owlNeo4j.get_entity_info_by_id(source['neoId'])
                        for prop in props:  # 添加属性，如果已经有同名关系出现，则该属性不添加
                            if any(prop == relation['name'] for relation in caches[source['neoId']]):
                                continue
                            flag = 0
                            if prop in keyword_list:
                                content = props[prop]
                                for sequence in sequence_list:
                                    if sequence[0] in content:
                                        target_sequence = sequence
                                        flag = 1
                                        break
                            if flag == 1:
                                num = 0
                                id = 0
                                for i in range(len(target_sequence)):
                                    num += 1
                                    if target_sequence[i] not in content:
                                        num = num - 1
                                        break
                                for i in range(num):
                                    if i < num - 1:
                                        start = content.index(target_sequence[i])
                                        end = content.index(target_sequence[i + 1])
                                        # target_content = content[start:end] if (end-start) <= 10 else content[start:start+10]+'...'
                                        caches[source['neoId']].append(
                                            {'name': prop, 'target_category': '属性值', 'target_name': content[start:end],
                                             'target_neoId': 100000 + id})
                                        id += 1
                                    else:
                                        start = content.index(target_sequence[i])
                                        # target_content = content[start:] if len(content[start:]) <= 10 else content[start:start+10]+'...'
                                        caches[source['neoId']].append(
                                            {'name': prop, 'target_category': '属性值', 'target_name': content[start:],
                                             'target_neoId': 100000 + id})
                                        id += 1
                            else:
                                # target_content = str(props[prop]) if len(str(props[prop])) <= 10 else str(props[prop])[0:10]+'...'
                                caches[source['neoId']].append(
                                    {'name': prop, 'target_category': '属性值', 'target_name': props[prop],
                                     'target_neoId': None})
                    # 对于所有关系属性逐个进行相似度匹配, 大于阈值就进行状态转移
                    link2state_map = {}
                    for link in caches[source['neoId']]:
                        score = serviceWord2vec.get_similarity(state['available_words'], list(jieba.cut(link['name'])))
                        if state['available_words'] == list(jieba.cut(link['name'])):
                            score = 1.0
                        if score == 1.0 and state['header']['score'] == 1.0:
                            # count += 1
                            # 如果之前没添加过同名关系，直接进行状态转移，记录跳转路径
                            if link['name'] not in link2state_map:
                                new_path = [step for step in state['path']]  # 用于处理多跳问题
                                if type(link['target_name']) == str and len(link['target_name']) > 10:
                                    name = link['target_name'][0:10] + '...'
                                else:
                                    name = link['target_name']
                                target = {'name': name, 'category': link['target_category'],
                                          'neoId': link['target_neoId'], 'title': link['target_name']}
                                new_path.append([source, link['name'], target])
                                new_score = state['score'] * (1 + score - threshold)
                                new_states.append(
                                    {'header': state['header'], 'tailer': target, 'available_words': [],
                                     'path': new_path,
                                     'score': new_score})
                                link2state_map[link['name']] = len(new_states) - 1
                            # 如果之前已经添加过一个同名关系，说明此关系是多值类(比如：知名校友)，直接把此关系追加到同名关系上
                            else:
                                state_num = link2state_map[link['name']]
                                new_tailer = new_states[state_num]['tailer'].copy()
                                new_tailer['neoId'] = None  # 如果此关系是多值类，则它不能再进行状态转移，所以把tailer neoId标记为None
                                new_states[state_num]['tailer'] = new_tailer
                                if type(link['target_name'] == str) and len(link['target_name']) > 10:
                                    name = link['target_name'][0:10] + '...'
                                else:
                                    name = link['target_name']
                                target = {'name': name, 'category': link['target_category'],
                                          'neoId': link['target_neoId'], 'title': link['target_name']}
                                new_states[state_num]['path'].append([source, link['name'], target])
            states += new_states
    if count > 0:
        return owlNeo4j.max_state(states)
    if len(questionlist) != 0:  # 存在可匹配的相似问题
        return  {'question':questionlist}
    # elif any(state['path'] != [] for state in states): # 存在完全匹配的问题
    #     return  owlNeo4j.max_state(states)
    else:
        answer = answer_from_attribute(states,threshold_3)
        if answer is not False:  # 能从属性值中找到相似语句
            return answer
        else:
            length = len(''.join(seg_list))
            name_list = ['']
            name_sum = 0
            for state in states:
                if state['header'] != None:
                    # logging.info('test' + state['header']['name'] + 'namesum' + str(name_sum))
                    if all((owlNeo4j.levenshtein(name, state['header']['name'])) < threshold_4 for name in name_list):
                        name_sum += len(state['header']['name'])
                        logging.info('namesum' + str(name_sum))
                        name_list.append(state['header']['name'])
            if all(state['header'] == None for state in states) or (((float(name_sum) / length) < threshold_4)):
                return answer_from_context(seg_list)
            else:
                max_states = []
                max_score = 0
                for state in states:
                    if state['score'] > max_score:
                        max_score = state['score']
                for state in states:
                    if state['score'] == max_score:
                        max_states.append(state)
                entities = [state['header'] for state in max_states if state['header'] is not None]
                neoid_list = []
                unique_entities = []
                score_map = {}
                for entity in entities:
                    if entity['neoId'] != None:
                        if 'score' in entity:
                            if entity['neoId'] not in score_map:
                                score_map[entity['neoId']] = entity['score']
                            else:
                                if score_map[entity['neoId']] < entity['score']:
                                    score_map[entity['neoId']] = entity['score']
                entities = sorted(entities, key=lambda x: score_map[x['neoId']], reverse=True)
                for entity in entities:
                    if entity['neoId'] not in neoid_list:
                            # entity['neoId'] = None
                        neoid_list.append(entity['neoId'])
                        del entity['score']
                        unique_entities.append(entity)
                # logging.info('max_states:' + json.dumps(max_states, ensure_ascii=False))
                # logging.info('unique_entities:' + json.dumps(unique_entities, ensure_ascii=False))
                # print "max:",max_states[0]['score']
                # if (max_states == []) or (max_states[0]['score'] == 1):  # 只识别到了实体
                #     if len(questionlist) != 0:  # 存在不完全匹配的实体和关系
                #         return {'ents': unique_entities, 'path': [], 'question': questionlist}
                #     else:
                return {'ents': unique_entities, 'path': []}  # 只存在实体（单一或多个）
                # else:
                #     paths = [state['path'] for state in max_states if state['header'] == entities[0]]
                #     return {'ents': [entities[0]], 'path': paths[0]}  # 1、（实体，关系，实体）；2、从属性值里找答案；3、全文检索

    # 对问句匹配不到任意一个实体，进行全文检索

# 按比较型问题
def autocom(question):
    namelist = []
    for name in owlNeo4j.name2num:
        namelist.append(name)
    result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}  # nodes表示展示结点的列表，links表示需要展示的关系，answerpath表示QA答案中结点的index（并非neoid）
    seg_list = segment(question)
    seg_list_complete = []
    for seg in seg_list:
        seg_list_complete.append(seg.word)
    relatedwords = [u'利率',u'产品利率',u'存款利率',u'贷款利率']
    word_1 = ''
    word_2 = ''
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
                num1 = float(word_1[word].strip('%'))
                num2 = float(word_2[word].strip("%"))
                break
        if num1 > num2 :
            answer = word_1['name']+'存款利率比'+word_2['name']+'高'+str((num1-num2))+"%"
        elif num1 < num2 :
            answer = word_1['name']+'存款利率比'+word_2['name']+'低'+str((num2-num1))+"%"
        else:
            answer = word_1['name']+'存款利率与'+word_2['name']+'一样高'
        result['answer'] = answer
        new_node1 = {'id': 0, 'name': word_1['name'], 'category': word_1['category'], 'neoId': word_1['neoId'], 'value': 0}
        new_node2 = {'id': 1, 'name': word_1[word], 'category': "属性值", 'neoId': None, 'value': 2}
        new_edge1 = {'id': 0, 'name': word, 'level': 1,'source':0,'target':1}
        result['nodes'].append(new_node1)
        result['nodes'].append(new_node2)
        new_node3 = {'id': 2, 'name': word_2['name'], 'category': word_2['category'], 'neoId': word_2['neoId'], 'value': 1}
        new_node4 = {'id': 3, 'name': word_2[word], 'category': "属性值", 'neoId': None, 'value': 3}
        new_edge2 = {'id': 1, 'name': word, 'level': 1,'source':2,'target':3}
        result['nodes'].append(new_node3)
        result['nodes'].append(new_node4)
        result['links'].append(new_edge1)
        result['links'].append(new_edge2)
        return result
    return 0
#按类别查询
def autocate(question):
    result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}
    category = question.split('c::')[1].strip()
    id = 0
    tag2num = {}
    kb = serviceKG.kb
    for node in kb:
        for tag in node['taglist'].split(','):
            if tag !='':
                score = owlNeo4j.entity_similarity(category,tag)
            if score >= 0.6:
               if tag not in tag2num:
                   tag2num[tag] = score
               else:
                   tag2num[tag] += 0.001  # 出现的次数越多，其排名越应该靠前。每多出现一次，权重加0.001
               new_node1 = node
               new_node2 = {'id': id, 'name': new_node1['name'], 'category': new_node1['category'],'neoId':new_node1['id'],'value': 0,'tag':new_node1['taglist'].split(',')[0]}
               result['nodes'].append(new_node2)
               id += 1
               break
    if len(result['nodes']) > 0:
        tag_list = list(sorted(tag2num.items(),key = lambda x:x[1],reverse=True))
        new_node2 = {'id': id, 'name': tag_list[0][0], 'category': '实体类别','neoId':None,'value': 0}
        result['nodes'].append(new_node2)
        for i in range(id):
              new_edge1 = {'id': i , 'name': result['nodes'][i]['tag'], 'level': 1,'source':i,'target':id}
              result['links'].append(new_edge1)
        result['answer'] = "为您找到 "+ tag_list[0][0] + " 类别下的实体"
        return result
    return 0
#按关系查询
def autolink(question):
    result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}
    relation = question.split('r::')[1]
    id = 0
    name2id = {}
    link2num = {}
    links = serviceKG.links
    if relation.find('<') == -1 :
        for link in links:
            score = serviceWord2vec.get_similarity(list(jieba.cut(relation)), list(jieba.cut(link['name'])))
            if relation == link['name']:
                score = 1.0
            if score >= 0.6:
                if link['name'] not in link2num:
                    link2num[link['name']] = score
                else:
                    link2num[link['name']] += 0.001  # 出现的次数越多，其排名越应该靠前。每多出现一次，权重加0.001
        relation_list = list(sorted(link2num.items(),key = lambda x : x[1],reverse = True))
        if len(relation_list) > 1:
            result['relation'] = []
            for num in range(len(relation_list)):
                result['relation'].append('r::' + relation_list[num][0] + '<' + str(num) + '>')
            print result['relation']
            return result
        else:
            if len(relation_list) == 1:
              for link in links:
                  if relation_list[0][0] == link['name']:
                        if id < 40 :
                            new_node1 = owlNeo4j.get_entity_info_by_id(link['source'])
                            new_node2 = owlNeo4j.get_entity_info_by_id(link['target'])
                            if (new_node1['name'] not in name2id) and (new_node2['name'] not in name2id):
                                new_edge1 = {'id': id , 'name': relation_list[0][0], 'level': 1,'source':id,'target':id+1}
                                result['nodes'].append({'id': id, 'name': new_node1['name'], 'category': new_node1['category'],'neoId':new_node1['neoId'],'value': 0})
                                result['nodes'].append({'id': id+1, 'name': new_node2['name'], 'category': new_node2['category'],'neoId':new_node2['neoId'],'value': 0})
                                result['links'].append(new_edge1)
                                name2id[new_node1['name']] = id
                                name2id[new_node2['name']] = id+1
                                id += 2
                            elif (new_node1['name'] not in name2id) and (new_node2['name']  in name2id):
                                new_edge1 = {'id': id , 'name': relation_list[0][0], 'level': 1,'source':id,'target':name2id[new_node2['name']]}
                                result['nodes'].append({'id': id, 'name': new_node1['name'], 'category': new_node1['category'],'neoId':new_node1['neoId'],'value': 0})
                                result['links'].append(new_edge1)
                                name2id[new_node1['name']] = id
                                id += 1
                            elif (new_node1['name']  in name2id) and (new_node2['name'] not in name2id):
                                new_edge1 = {'id': id , 'name': relation_list[0][0], 'level': 1,'source':name2id[new_node1['name']],'target':id}
                                result['nodes'].append({'id': id, 'name': new_node2['name'], 'category': new_node2['category'],'neoId':new_node1['neoId'],'value': 0})
                                result['links'].append(new_edge1)
                                name2id[new_node2['name']] = id
                                id += 1
                            else:
                                new_edge1 = {'id': id , 'name': relation_list[0][0], 'level': 1,'source':name2id[new_node1['name']],'target':name2id[new_node2['name']]}
                                result['links'].append(new_edge1)
              result['answer'] = "为您找到具有 "+ relation_list[0][0] + " 关系的实体对"
              return result
    else:
        index = relation.find('<')
        relation = relation[0:index]
        for link in links:
            if relation == link['name']:
                if id < 40 :
                    new_node1 = owlNeo4j.get_entity_info_by_id(link['source'])
                    new_node2 = owlNeo4j.get_entity_info_by_id(link['target'])
                    if (new_node1['name'] not in name2id) and (new_node2['name'] not in name2id):
                        new_edge1 = {'id': id , 'name': relation, 'level': 1,'source':id,'target':id+1}
                        result['nodes'].append({'id': id, 'name': new_node1['name'], 'category': new_node1['category'],'neoId':new_node1['neoId'],'value': 0})
                        result['nodes'].append({'id': id+1, 'name': new_node2['name'], 'category': new_node2['category'],'neoId':new_node2['neoId'],'value': 0})
                        result['links'].append(new_edge1)
                        name2id[new_node1['name']] = id
                        name2id[new_node2['name']] = id+1
                        id += 2
                    elif (new_node1['name'] not in name2id) and (new_node2['name']  in name2id):
                        new_edge1 = {'id': id , 'name': relation, 'level': 1,'source':id,'target':name2id[new_node2['name']]}
                        result['nodes'].append({'id': id, 'name': new_node1['name'], 'category': new_node1['category'],'neoId':new_node1['neoId'],'value': 0})
                        result['links'].append(new_edge1)
                        name2id[new_node1['name']] = id
                        id += 1
                    elif (new_node1['name']  in name2id) and (new_node2['name'] not in name2id):
                        new_edge1 = {'id': id , 'name': relation, 'level': 1,'source':name2id[new_node1['name']],'target':id}
                        result['nodes'].append({'id': id, 'name': new_node2['name'], 'category': new_node2['category'],'neoId':new_node2['neoId'],'value': 0})
                        result['links'].append(new_edge1)
                        name2id[new_node2['name']] = id
                        id += 1
                    else:
                        new_edge1 = {'id': id , 'name': relation, 'level': 1,'source':name2id[new_node1['name']],'target':name2id[new_node2['name']]}
                        result['links'].append(new_edge1)
        result['answer'] = "为您找到具有 "+ relation + " 关系的实体对"
        return result

#归纳类问题
def autoinduce(question):
    seg_list = segment(question)
    seg_list_complete = []
    flag = 0
    catelist = serviceKG.catelist
    num_dict = serviceKG.num_dict
    kb = serviceKG.kb
    for seg in seg_list:
        seg_list_complete.append(seg.word)
        if seg.word in [u'利率',u'产品利率',u'存款利率',u'贷款利率']:
            flag = 1
            related_word = seg.word
    if flag == 1 :
        for seg in seg_list_complete:
            if flag == 1:
                for tag in catelist:
                    if seg == tag:
                        flag = 2
                        tagname = seg
                        break
            else :
                break
    if flag == 2:
        for seg in seg_list_complete:
            if seg in num_dict:
                num = seg
                flag = 3
                break
    if flag == 3:
        result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}
        allnodes = []
        for node in kb:
            if (tagname in node['taglist']) and (related_word in node):
               new_node1 = owlNeo4j.get_entity_list_by_name(node['name'])[0]
               allnodes.append(new_node1)
        if len(allnodes) >= (num_dict[num]+1):
            sortlist = [0 for x in range(len(allnodes))]
            result_list = sorted(allnodes,key=lambda x : float(x[related_word].strip('%')),reverse=True)
            for number in range(1,len(result_list)):
                if float(result_list[number][related_word].strip('%')) == float(result_list[number-1][related_word].strip('%')):
                     sortlist[number] = sortlist[number-1]
                else:
                     sortlist[number] = sortlist[number-1] + 1
            num1 = num_dict[num]
            id = 0
            name = ''
            for i in range(len(sortlist)):
                if num1 == sortlist[i]:
                    targetnode = result_list[i]
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 0}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 1}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    result['answerpath'].append(id)
                    result['answerpath'].append(id+1)
                    id += 2
                    name = name + result_list[i]['name'] +'、'
                else :
                    targetnode = result_list[i]
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 1}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 2}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    id += 2
            result['answer'] = tagname + ' 中' + related_word + num + '的是' + name[:-1]
            return result
    return 0
#检索型问题
def autoret(question):
    seg_list = segment(question)
    seg_list_complete = []
    catelist = serviceKG.catelist
    kb = serviceKG.kb
    flag = 0
    for seg in seg_list:
        seg_list_complete.append(seg.word)
        if seg.word in [u'利率',u'产品利率',u'存款利率',u'贷款利率']:
            flag = 1
            related_word = seg.word
    if flag == 1 :
        for seg in seg_list_complete:
            if flag == 1:
                for tag in catelist:
                    if seg == tag:
                        flag = 2
                        tagname = seg
                        break
            else :
                break
    if flag == 2:
        for seg in seg_list_complete:
            if seg in [u'高于',u'低于',u'等于']:
                mark = seg
                flag = 3
                break
    if flag == 3:
        for seg in seg_list:
            if seg.flag == 'm':
                if len(seg_list) >= seg_list.index(seg)+2:
                    if seg_list[seg_list.index(seg)+1].word == u'%':
                        num = float(seg.word)
                        #print num
                    else :
                        num = float(seg.word)*100
                else :
                    num = float(seg.word)*100
                flag = 4
                break
    if flag == 4:
        result = {'nodes': [], 'links': [], 'answerpath': [], 'answerlist': []}
        allnodes = []
        id = 0
        name = ''
        for node in kb:
            if (tagname in node['taglist']) and (related_word in node):
               new_node1 = owlNeo4j.get_entity_list_by_name(node['name'])[0]
               allnodes.append(new_node1)
        if mark == u'高于':
            for node in allnodes:
                if  float(node[related_word].strip('%')) > num:
                    targetnode = node
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 0}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 1}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    result['answerpath'].append(id)
                    result['answerpath'].append(id+1)
                    name = name + targetnode['name'] +'、'
                    id += 2
                else :
                    targetnode = node
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 1}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 2}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    id += 2
        elif mark == u'低于' :
            for node in allnodes:
                if  float(node[related_word].strip('%')) < num:
                    targetnode = node
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 0}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 1}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    result['answerpath'].append(id)
                    result['answerpath'].append(id+1)
                    name = name + targetnode['name'] +'、'
                    id += 2
                else :
                    targetnode = node
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 1}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 2}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    id += 2
        else :
            for node in allnodes:
                if num == float(node[related_word].strip('%')):
                    targetnode = node
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 0}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 1}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    result['answerpath'].append(id)
                    result['answerpath'].append(id+1)
                    name = name + targetnode['name'] +'、'
                    id += 2
                else :
                    targetnode = node
                    new_node2 = {'id': id, 'name': targetnode['name'], 'category': targetnode['category'],'neoId':targetnode['neoId'],'value': 1}
                    new_node3 = {'id': id+1, 'name': targetnode[related_word], 'category': "属性值", 'neoId': None, 'value': 2}
                    new_edge1 = {'id': id, 'name': related_word, 'level': 1,'source':id,'target':id+1}
                    result['nodes'].append(new_node2)
                    result['nodes'].append(new_node3)
                    result['links'].append(new_edge1)
                    id += 2
        if len(result['answerpath']) > 0:
             result['answer'] = tagname + ' 中' + related_word + mark + str(num) + '%' + '的有' + name[:-1]
        else :
            result['answer'] = tagname + ' 中不存在' + related_word + mark + str(num) + '%' + '的产品'
        return result
    return 0
#流程类问题
def autoseq(question):
    word2sent = {}
    namelist = []
    # candidate_answer = ["","",0]  #0:attribute name; 1:answer; 2:score
    for name in owlNeo4j.name2num:
        namelist.append(name)
    for word in queryword_list:
        question = question.replace(word,'')
    for punctuation in punctuation_list:
        question = question.replace(punctuation,'')
    # print question
    seg_list = segment(question)
    for word in seg_list:
        if word.flag == 'x' and (word.word in namelist):
            if word.word not in word2sent:
                # seg_list_back = seg_list.copy()
                word2sent[word.word] = seg_list
                # print 'word',word.word
                # print "seg_list_1",seg_list.remove(word)
                # print "seg_list_2",word2sent[word.word]
                # seg_list = seg_list_back
                # break  # 此处为了限制只查询一个实体，但是显然是不正确的，周一展示后修改
    # for word in word2sent:
    #     print 'word:',word
    print
    if len(word2sent) >= 1 :
        max_point = 0.0
        opt_answer = ''
        opt_node = {}
        for word in word2sent:
            attri_value_list = []
            seg_list_complete = [seg.word for seg in word2sent[word]]
            node = owlNeo4j.get_entity_list_by_name(word)[0]
            for attribute in node.keys():
                    if attribute  in keyword_list:
                        attri_value = node[attribute]
                        attri_value_list.append(attri_value)
            if len(attri_value_list) > 0:
                res = attributeMatch_seq.answer_selection_by_attextract_TFIDF_allAttribute(seg_list_complete, attri_value_list, answer_num=1) #默认返回3条答案，可以通过answer_num设置
                if res['point'] > max_point :
                    # print 'answer:',res['answer']
                    opt_answer = res['answer'].decode('unicode-escape')
                    max_point = float(res['point'])
                    opt_node = node
        if max_point > 0.0:
            abstract = opt_answer if len(opt_answer) < 10 else opt_answer[:10] + '...'
            new_path = []
            source = {'name': opt_node['name'], 'category': opt_node['category'],
                      'neoId': opt_node['neoId']}
            target = {'name': abstract, 'category': '实体描述文本', 'neoId': None, 'ans_from_desc': opt_answer}
            new_path.append([source, '候选答案', target])
            # print 'nodename:',node['name']
            return {'ents':[opt_node],'path':new_path}
        else:
            return 0
    else:
        return 0
#动态规划1 question
def dynamic_planning_question(seg_list):
    threshold = 0.6  # 向量相似度匹配的状态转移阈值
    threshold_2 = 0.3  # 关系相似度（编辑距离）的转移阈值
    threshold_3 = 0.4  # 文本答案选择匹配的状态转移阈值
    threshold_4 = 0.6  # 在只查找到实体的情况下，实体名长度占问题长度的比例转移阈值
    true_question = {}
    questionlist = []
    states = []
    caches = {}
    label = 1
    for word in seg_list:
        new_states = []
        states.append({'header': None, 'tailer': None, 'available_words': [], 'path': [], 'score': 0})
        for state in states:
            state['available_words'].append(word)
            # 对于START状态
            if (state['header'] is None):
                entity_name = "".join(state['available_words'])
                same_name_entity_list = owlNeo4j.get_entity_list_by_name(entity_name)
                for entity in same_name_entity_list:
                    new_states.append({'header': entity, 'tailer': None, 'available_words': [], 'path': [], 'score': 1})
            # 对于非START状态
            else:
                if state['tailer'] is None:
                    source = {'name': state['header']['name'], 'category': state['header']['category'],
                              'neoId': state['header']['neoId']}
                else:
                    source = state['tailer']
                if source['neoId'] is None:  # neoId is None 意味着路径走到了一个不可跳转的状态
                    continue
                if source['neoId'] not in caches:  # 整理这个实体的关系与属性集，加入到缓存中等待使用
                    caches[source['neoId']] = []
                    relations = owlNeo4j.get_oneway_related_entities_by_id(source['neoId'])
                    for relation in relations:  # 添加关系
                        caches[source['neoId']].append(relation)
                    props = owlNeo4j.get_entity_info_by_id(source['neoId'])
                    for prop in props:  # 添加属性，如果已经有同名关系出现，则该属性不添加
                        if any(prop == relation['name'] for relation in caches[source['neoId']]):
                            continue
                        flag = 0
                        if prop in keyword_list:
                            content = props[prop]
                            for sequence in sequence_list:
                                if sequence[0] in content:
                                    target_sequence = sequence
                                    flag = 1
                                    break
                        if flag == 1:
                            num = 0
                            id = 0
                            for i in range(len(target_sequence)):
                                num += 1
                                if target_sequence[i] not in content:
                                    num = num - 1
                                    break
                            for i in range(num):
                                if i < num - 1:
                                    start = content.index(target_sequence[i])
                                    end = content.index(target_sequence[i + 1])
                                    # target_content = content[start:end] if (end-start) <= 10 else content[start:start+10]+'...'
                                    caches[source['neoId']].append(
                                        {'name': prop, 'target_category': '属性值', 'target_name': content[start:end],
                                         'target_neoId': 100000 + id})
                                    id += 1
                                else:
                                    start = content.index(target_sequence[i])
                                    # target_content = content[start:] if len(content[start:]) <= 10 else content[start:start+10]+'...'
                                    caches[source['neoId']].append(
                                        {'name': prop, 'target_category': '属性值', 'target_name': content[start:],
                                         'target_neoId': 100000 + id})
                                    id += 1
                        else:
                            # target_content = str(props[prop]) if len(str(props[prop])) <= 10 else str(props[prop])[0:10]+'...'
                            caches[source['neoId']].append(
                                {'name': prop, 'target_category': '属性值', 'target_name': props[prop],
                                 'target_neoId': None})
                # 对于所有关系属性逐个进行相似度匹配, 大于阈值就进行状态转移
                link2state_map = {}
                for link in caches[source['neoId']]:
                    score = serviceWord2vec.get_similarity(state['available_words'], list(jieba.cut(link['name'])))
                    if state['available_words'] == list(jieba.cut(link['name'])):
                        score = 1.0
                    if score >= threshold:
                        if owlNeo4j.levenshtein(link['name'], ''.join(state['available_words'])) >= threshold_2 or (
                                u'是什么' == ''.join(state['available_words'])):
                            value = state['header']['score'] * score
                            question = state['header']['name'] + '的' + link['name'] + '是什么'
                            if question not in true_question:
                                true_question[question] = value
                            else:
                                if value > true_question[question]:
                                    true_question[question] = value
        states += new_states
    if true_question is not None:
        true_question = list(sorted(true_question.items(), key=lambda x: x[1], reverse=True))
        for question in true_question:
            questionlist.append(str(label) + '.' + question[0])
            label += 1
    return questionlist

#动态规划2 answer
def dynamic_planning_answer(seg_list):
    threshold = 0.6  # 向量相似度匹配的状态转移阈值
    threshold_2 = 0.3  # 关系相似度（编辑距离）的转移阈值
    threshold_3 = 0.4  # 文本答案选择匹配的状态转移阈值
    threshold_4 = 0.6  # 在只查找到实体的情况下，实体名长度占问题长度的比例转移阈值
    true_question = {}
    questionlist = []
    states = []
    caches = {}
    seg_list = seg_list[1:]
    for word in seg_list:
        logging.info("seg_list:" + '/'.join(seg_list))
        new_states = []
        states.append({'header': None, 'tailer': None, 'available_words': [], 'path': [], 'score': 0})
        for state in states:
            state['available_words'].append(word)
            # 对于START状态
            if (state['header'] is None):
                entity_name = "".join(state['available_words'])
                same_name_entity_list = owlNeo4j.get_entity_list_by_name(entity_name)
                for entity in same_name_entity_list:
                    new_states.append(
                        {'header': entity, 'tailer': None, 'available_words': [], 'path': [], 'score': 1})
            # 对于非START状态
            else:
                if state['tailer'] is None:
                    source = {'name': state['header']['name'], 'category': state['header']['category'],
                              'neoId': state['header']['neoId']}
                else:
                    source = state['tailer']
                if source['neoId'] is None:  # neoId is None 意味着路径走到了一个不可跳转的状态
                    continue
                if source['neoId'] not in caches:  # 整理这个实体的关系与属性集，加入到缓存中等待使用
                    caches[source['neoId']] = []
                    relations = owlNeo4j.get_oneway_related_entities_by_id(source['neoId'])
                    for relation in relations:  # 添加关系
                        caches[source['neoId']].append(relation)
                    props = owlNeo4j.get_entity_info_by_id(source['neoId'])
                    for prop in props:  # 添加属性，如果已经有同名关系出现，则该属性不添加
                        if any(prop == relation['name'] for relation in caches[source['neoId']]):
                            continue
                        flag = 0
                        if prop in keyword_list:
                            content = props[prop]
                            for sequence in sequence_list:
                                if sequence[0] in content:
                                    target_sequence = sequence
                                    flag = 1
                                    break
                        if flag == 1:
                            num = 0
                            id = 0
                            for i in range(len(target_sequence)):
                                num += 1
                                if target_sequence[i] not in content:
                                    num = num - 1
                                    break
                            for i in range(num):
                                if i < num - 1:
                                    start = content.index(target_sequence[i])
                                    end = content.index(target_sequence[i + 1])
                                    # target_content = content[start:end] if (end-start) <= 10 else content[start:start+10]+'...'
                                    caches[source['neoId']].append(
                                        {'name': prop, 'target_category': '属性值', 'target_name': content[start:end],
                                         'target_neoId': 100000 + id})
                                    id += 1
                                else:
                                    start = content.index(target_sequence[i])
                                    # target_content = content[start:] if len(content[start:]) <= 10 else content[start:start+10]+'...'
                                    caches[source['neoId']].append(
                                        {'name': prop, 'target_category': '属性值', 'target_name': content[start:],
                                         'target_neoId': 100000 + id})
                                    id += 1
                        else:
                            # target_content = str(props[prop]) if len(str(props[prop])) <= 10 else str(props[prop])[0:10]+'...'
                            caches[source['neoId']].append(
                                {'name': prop, 'target_category': '属性值', 'target_name': props[prop],
                                 'target_neoId': None})
                # 对于所有关系属性逐个进行相似度匹配, 大于阈值就进行状态转移
                link2state_map = {}
                for link in caches[source['neoId']]:
                    score = serviceWord2vec.get_similarity(state['available_words'], list(jieba.cut(link['name'])))
                    if state['available_words'] == list(jieba.cut(link['name'])):
                        score = 1.0
                    if score == 1.0 and state['header']['score'] == 1.0:
                        # count += 1
                        # 如果之前没添加过同名关系，直接进行状态转移，记录跳转路径
                        if link['name'] not in link2state_map:
                            new_path = [step for step in state['path']]  # 用于处理多跳问题
                            if type(link['target_name']) == str and len(link['target_name']) > 10:
                                name = link['target_name'][0:10] + '...'
                            else:
                                name = link['target_name']
                            target = {'name': name, 'category': link['target_category'],
                                      'neoId': link['target_neoId'], 'title': link['target_name']}
                            new_path.append([source, link['name'], target])
                            new_score = state['score'] * (1 + score - threshold)
                            new_states.append(
                                {'header': state['header'], 'tailer': target, 'available_words': [],
                                 'path': new_path,
                                 'score': new_score})
                            link2state_map[link['name']] = len(new_states) - 1
                        # 如果之前已经添加过一个同名关系，说明此关系是多值类(比如：知名校友)，直接把此关系追加到同名关系上
                        else:
                            state_num = link2state_map[link['name']]
                            new_tailer = new_states[state_num]['tailer'].copy()
                            new_tailer['neoId'] = None  # 如果此关系是多值类，则它不能再进行状态转移，所以把tailer neoId标记为None
                            new_states[state_num]['tailer'] = new_tailer
                            if type(link['target_name'] == str) and len(link['target_name']) > 10:
                                name = link['target_name'][0:10] + '...'
                            else:
                                name = link['target_name']
                            target = {'name': name, 'category': link['target_category'],
                                      'neoId': link['target_neoId'], 'title': link['target_name']}
                            new_states[state_num]['path'].append([source, link['name'], target])
        states += new_states
    return states

#从属性值中抽取答案(word2vec+tf-idf)
def answer_from_attribute(states,threshold_3):
    visited_states = set()
    attri_states = []
    entity_count = 0  # 已抽取实体计数
    for state in states:
        candidate_answer = ["", "", 0]  # 0:attribute name; 1:answer; 2:score
        attri_value_list = []
        if (state['header'] is not None) and (state['available_words'] != []) and (
                state['header']['neoId'] not in visited_states) and entity_count <= 5:
            visited_states.add(state['header']['neoId'])
            entity_count += 1
            for attribute in state['header'].keys():
                if attribute not in config.not_extract_attributes:
                    attri_value = str(state['header'][attribute])
                    # res = owlSubServers.answer_selection(str(''.join(state['available_words'])), str(attri_value))
                    attri_value_list.append(attri_value)
            logging.info('entity name: ' + state['header']['name'])
            res = attributeMatch.answer_selection_by_TFIDF_allAttribute_word2vec_hasmostword(state['available_words'],
                                                                                             attri_value_list,
                                                                                             tfidf_threshold=threshold_3)  # 默认返回3条答案，可以通过answer_num设置
            if res is not None:
                # print 'answer exists.',res
                answer = res['answer'].decode('unicode-escape')
                point = float(res['point'])
                # candidate_answer[0] = attribute
                # candidate_answer[1] = answer
                candidate_answer[2] = point
                # answer = candidate_answer[1]
                abstract = answer if len(answer) < 10 else answer[:10] + '...'
                new_path = []
                source = {'name': state['header']['name'], 'category': state['header']['category'],
                          'neoId': state['header']['neoId']}
                target = {'name': abstract, 'category': '实体描述文本', 'neoId': None, 'ans_from_desc': answer}
                new_path.append([source, '候选答案', target])
                new_score = candidate_answer[2]
                attri_states.append(
                    {'header': state['header'], 'tailer': target, 'available_words': [], 'path': new_path,
                     'score': new_score})
    if len(attri_states) != 0:
        return owlNeo4j.max_state(attri_states)
    else:
        return False

#全文检索
def answer_from_context(seg_list):
    text_states = []
    res = textSearch.find_answer_in_text_bank(seg_list)
    # logging.info('res:' + json.dumps(res, encoding='utf-8', ensure_ascii=False))
    candidate_answer = ["", "", 0]  # 0:attribute name; 1:answer; 2:score
    if res is not None:
        answer = res['answer'].decode('unicode-escape')
        point = float(res['point'])
        # candidate_answer[0] = attribute
        # candidate_answer[1] = answer
        candidate_answer[2] = point
        # answer = candidate_answer[1]
        abstract = answer if len(answer) < 10 else answer[:20] + '...'
        new_path = []
        global out_question
        source = {'name': '知识库检索问题', 'category': '文本检索', 'neoId': None, '问题': out_question}
        target = {'name': abstract, 'category': '文本检索答案', 'neoId': None, 'ans_from_desc': answer}
        new_path.append([source, '候选答案', target])
        new_score =  candidate_answer[2]
        text_states.append(
            {'header': source, 'tailer': target, 'available_words': [], 'path': new_path,
             'score': new_score})
        return owlNeo4j.max_state(text_states)
    else:
        return False

# 分词
def segment(sentence):
    fliter_list = config.stop_words
    seg_list_unflit = list(posseg.cut(sentence))  # posseg.cut返回的是一个生成器，每一项包括分词及标注
    seg_list_flit = []
    for word in seg_list_unflit:
        if word.word not in fliter_list:
            seg_list_flit.append(word)
    return seg_list_flit

