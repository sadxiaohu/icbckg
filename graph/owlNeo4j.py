# coding=utf-8
import urllib2
import json
import icbckg.config as config
import serviceQA

print ("Loading data:icbc kg ......")
kb = json.load(open(config.KB_path))
id2num = {}
name2num = {}
nodes = kb['nodes']
index_dict = {}  # 建立一个以实体名称长度为索引的索引表
max_len = 1 #所有实体中最长的实体名长度
for node in nodes:
    name,name_len = node['name'],len(node['name'])
    if name_len > max_len:
        max_len = name_len
    if name_len not in index_dict:
        index_dict[name_len] = []
    index_dict[name_len].append(name)
# print('max_len',max_len,'index_dict',index_dict[5])
for i, node in enumerate(kb['nodes']):
    node['neoId'] = int(node['id'])
    del node['id']
    if 'category' not in node:
        node['category'] = '其他'
    if node['neoId'] not in id2num:#建立neoid到索引的映射
        id2num[node['neoId']] = i
    if node['name'] not in name2num:#建立name到索引的映射，如果存在同名实体，则映射到同名实体所在的所有索引
        name2num[node['name']] = [i]
    else:
        name2num[node['name']].append(i)
for link in kb['links']:
    link['source'] = int(link['source'])
    link['target'] = int(link['target'])

def get_entity_info_by_id(neoid):#通过neoid获得实体
    if neoid in id2num:
        return kb['nodes'][id2num[neoid]]
    return None


def get_entity_list_by_name(name):#通过name获得实体，有可能有多个同名实体
    if name in name2num:
        answer_list = []
        for num in name2num[name]:
            answer = kb['nodes'][num].copy()
            answer['score'] = 1.0
            answer_list.append(answer)
        return answer_list
    else:
        return get_entity_list_by_fuzzy_name(name)


def get_entity_list_by_fuzzy_name(name):#模糊实体名的匹配
    entity_list = []
    score_map = {}
    threshold = 0.6
    amount = 0
    name_len = len(name)
    if name_len > max_len:
        return entity_list
    max_len_true = min(int(name_len*5.0/3),max_len)
    # print name,max_len_true
    for lens in range(name_len,max_len_true+1):
      if lens in index_dict:
        name_list = index_dict[lens]
        for name_full in name_list:
            true_name = name_full
            flag = 0
            name_full_len = len(name_full)
            if name in name_full:
                flag = 1
                score = float(name_len)/name_full_len
                # if lens <= 5:
                #   print 'flag==1',true_name,score
            else:
                count = 0
                for word in name:
                    if word in name_full:
                        count += 1
                        name_full = name_full.replace(word,'',1)
                score = float(count)/name_full_len
            if score >= threshold:
                    for num in name2num[true_name]:
                        amount += 1
                        answer = kb['nodes'][num]
                        answer['score'] = score
                        entity_list.append(answer)
                        if flag == 1:
                           score_map[kb['nodes'][num]['neoId']] = score+0.2
                        else:
                           score_map[kb['nodes'][num]['neoId']] = score
    entity_list = sorted(entity_list, key=lambda l:score_map[l['neoId']], reverse=True)
    return entity_list[0:10] if len(entity_list)>10 else entity_list

def entity_similarity(name,name_full):
    if (name in name_full) or (name_full in name) :
                score = min(float(len(name))/len(name_full),float(len(name_full))/len(name))
                return score
    else:
        count = 0
        if len(name) <= len(name_full):
                for word in name:
                    if word in name_full:
                        count += 1
                score = float(count*1.0/len(name_full))
                return score
        else:
           for word in name_full :
                    if word in name:
                        count += 1
           score = float(count*1.0/len(name))
           return score


def get_oneway_related_entities_by_id(neoid,max_num = 10):#返回一个源实体与其所有的目标实体
    neoid = int(neoid)
    related_entities = []
    for link in kb['links']:
        if link['source'] == neoid:
            node_t = kb['nodes'][id2num[link['target']]]
            related_entities.append({'name': link['name'], 'target_category': node_t['category'], 'target_name': node_t['name'],
                         'target_neoId': node_t['neoId'], 'positive': True})
        if max_num is not None:
            if len(related_entities) > max_num:
                break
    return related_entities


def get_twoway_related_entities_by_id(neoid, max_num = 10):#返回一个实体与其有联系的所有目标实体，该实体既可以是源实体也可以是目标实体
    neoid = int(neoid)
    related_entities = []
    for link in kb['links']:
        if link['source'] == neoid:
            node_t = kb['nodes'][id2num[link['target']]]
            related_entities.append({'name': link['name'], 'target_category': node_t['category'], 'target_name': node_t['name'],
                         'target_neoId': node_t['neoId'], 'positive': True})
        if link['target'] == neoid:
            node_t = kb['nodes'][id2num[link['source']]]
            related_entities.append({'name': link['name'], 'target_category': node_t['category'], 'target_name': node_t['name'],
                         'target_neoId': node_t['neoId'], 'positive': False})
        if max_num is not None:
            if len(related_entities) > max_num:
                break
    return related_entities

#动态规划实现莱文斯坦距离
def levenshtein(string1,string2):
    if len(string1) > len(string2):
        string1,string2 = string2,string1
    if len(string1) == 0:
        return 0
    if len(string2) == 0:
        return 0
    str1_length = len(string1) + 1
    str2_length = len(string2) + 1
    distance_matrix = [list(range(str2_length)) for x in range(str1_length)]
    # print(distance_matrix)
    for i in range(1,str1_length):
        for j in range(1,str2_length):
            deletion = distance_matrix[i-1][j] + 1  # 删除string1的第i个字符，也可看做将string1的第i个字符插入string2的后面
            insertion = distance_matrix[i][j-1] + 1  # 将string2的第j个字符插入到string1的后面，也可以看做删除string2的第j个字符
            substitution = distance_matrix[i-1][j-1]  # 替换
            if string1[i-1] != string2[j-1]:   # 字符串的第i个字符和第j个字符相等
                substitution += 1
            distance_matrix[i][j] = min(insertion,deletion,substitution)
    # print(distance_matrix[str1_length-1][str2_length-1])
    # print(1-0.8)由于浮点数字精度问题，采用四舍五入
    return round(1-float(distance_matrix[str1_length-1][str2_length-1])/max(len(string1),len(string2)),2)

#取出得分最大的一组（或一个）state
def max_state(states):
    max_states = []
    max_score = 0
    for state in states:
        if state['score'] > max_score:
            max_score = state['score']
    for state in states:
        if state['score'] == max_score:
            max_states.append(state)
    entities = [state['header'] for state in max_states if state['header'] is not None]
    paths = [state['path'] for state in max_states if state['header'] == entities[0]]
    return {'ents': [entities[0]], 'path': paths[0]}

def get_max_id_in_nodes():
    ids = [int(node['id']) for node in kb['nodes']]
    return max(ids)

def get_max_id_in_links():
    ids = [int(link['id']) for link in kb['links']]
    return max(ids)
