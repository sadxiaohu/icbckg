# -*- coding: utf-8 -*-
#__author__:lxf

from dataAnalysis import entityAnalysis
import codecs
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def kg_preprocess(kg): #知识库预处理：确保知识库中存在nodes，links，每个nodes中都存在唯一id，name，taglist
    if 'nodes' not in kg.keys():
        kg['nodes'] = []
    if 'links' not in kg.keys():
        kg['links'] = []
    exist_ids = []
    for entity in kg['nodes']:
        if 'id' not in entity.keys():
            print('entity:', str(entity), 'has no id property!')
            raise Exception('entity has no id property!')
        else:
            if entity['id'] in exist_ids:
                raise Exception('there are two or more same entity ids!')
            else:
                exist_ids.append(entity['id'])
        if 'name' not in entity.keys():
            print('entity:', str(entity), 'has no name property!')
            raise Exception('entity has no name property!')
        if 'taglist' not in entity.keys():
            entity['taglist'] = ''
    return kg

def kg_links_reIndex(kg_links, start_link_id):
    for link in kg_links:
        link['id'] = start_link_id
        start_link_id += 1
    return kg_links

def find_same_name_entities_when_only_name(basic_kg, other_kg):  #当两个知识库中的实体名都不重复时调用此方法
    result = {}
    for basic_entity in basic_kg['nodes']:
        for other_entity in other_kg['nodes']:
            if basic_entity['name'] == other_entity['name']:
                result[basic_entity['name']] = [basic_entity, other_entity]
                break
    return result

def entities_fution(kg, need_2_fution_entities):
    '''
    对一个知识库中进行已知需要融合实体的融合, 注意need_2_fution_entities的格式：
    {
	"自动柜员机": [
		{
			"name": "自动柜员机",
			...
		},
		{
			"name": "自动柜员机",
			...
		}
	],
	...
	}
	出现在同名实体list中的元素，靠前的第一个作为融合的基准，其他实体的属性增量加入第一个中，find_same_name_entities_when_only_name返回内容形式同此。
    :param kg:
    :param need_2_fution_entities: 需要融合的实体列表，可以是同名实体，也可以是相近实体，在另外方法中确定需要融合的实体集
    :return:
    '''
    all_entities = kg['nodes'] #list
    all_links = kg['links'] #list
    for same_name_entities in need_2_fution_entities.values():
        new_entity = {}
        for i in range(len(same_name_entities)):
            if i == 0:
                new_entity = same_name_entities[i]
                taglist = new_entity['taglist']
                tag_list = taglist.split(',')
                if tag_list[0].endswith(u'分行'):
                    tag_list.pop(0)
                    taglist = ','.join(tag_list)
                    new_entity['taglist'] = taglist
            else:
                origin_entity = same_name_entities[i]  #prcess entity
                for origin_key in origin_entity.keys():
                    if origin_key not in new_entity.keys():
                        new_entity[origin_key] = origin_entity[origin_key]
                    elif origin_key == u'常见问题':
                        new_entity[origin_key] += origin_entity[origin_key]
                    # else:
                    #     if len(new_entity[origin_key]) < len(origin_entity[origin_key]):
                    #         new_entity[origin_key] = origin_entity[origin_key]

                #delete origin entity, process links
                new_id = new_entity['id']
                origin_id = origin_entity['id']
                for entity in all_entities: #delete entity
                    if entity['id'] == origin_id:
                        all_entities.remove(entity)
                        break
                for link in all_links:  #link-->dict
                    if link['source'] == int(origin_id):
                        link['source'] = int(new_id)
                    if link['target'] == int(origin_id):
                        link['target'] = int(new_id)
        for entity in all_entities:  # delete entity
            if entity['id'] == new_entity['id']:
                all_entities.remove(entity)
                all_entities.append(new_entity)
                break
    result = {}
    result['nodes'] = all_entities
    result['links'] = all_links
    return result

def other_kg_add_into_basic_kg(basic_kg, other_kg, basic_kg_link_propertes=None, other_kg_link_propertes=None, find_self_links_method=None, find_two_kg_links_method=None,
                               find_same_entities_method=None):
    '''
    知识库中增加新的知识，包括同名实体融合，关系发现和扩展, 默认已经完成了新知识库的id递增产生,新知识库可以包含和不包含links，下面会根据参数：other_kg_link_propertes
    来进行一次新知识库的自身链接构建，之后再进行新旧知识库之间的链接补全，最后进行同名实体的融合操作。
    同名实体融合时：要求另外构造一个字典用于同名实体的融合，字典结构见：same_name_entities_fution（）
    :param basic_kg:已有的知识库
    :param other_kg:欲融合知识库
    :param basic_kg_link_propertes:已有知识库链接构造时依据的属性集合
    :param other_kg_link_propertes:新知识库链接构造时依据的属性集合
    :param find_self_links_method:新知识库发掘自身链接的方法，配合other_kg_link_propertes属性使用
    :param find_two_kg_links_method:新旧知识库实体发掘链接方法，配合basic_kg_link_propertes，other_kg_link_propertes使用
    :param find_same_entities_method: 发现两个知识库中同名实体的方法！  特别注意：这是方法名，不是变量！ 调用时具体情况调用不同的方法
    :return:
    '''
    kg_preprocess(other_kg)
    if len([entity for entity in basic_kg['nodes'] if entity['id'] in
                [inner_entity['id'] for inner_entity in other_kg['nodes']]]):
        raise Exception('has the same entity id in two kgs !')
    if len([entity for entity in basic_kg['links'] if entity['id'] in
                [inner_entity['id'] for inner_entity in other_kg['links']]]):
        print('there are same link ids in two kgs !')
        if len(basic_kg['links']):
            max_basic_link_id = int(sorted(basic_kg['links'], key=lambda link: int(link['id']), reverse=True)[0]['id']) + 1
        else:
            max_basic_link_id = 0
        other_kg['lniks'] = kg_links_reIndex(other_kg['links'], max_basic_link_id)
    if find_self_links_method:
        if len(basic_kg['links']):
            max_basic_link_id = int(sorted(basic_kg['links'], key=lambda link: int(link['id']), reverse=True)[0]['id']) + 1
        else:
            max_basic_link_id = 0
        if len(other_kg['links']):
            max_other_link_id = int(sorted(other_kg['links'], key=lambda link: int(link['id']), reverse=True)[0]['id']) + 1
        else:
            max_other_link_id = 0
        if max_basic_link_id >= max_other_link_id:
            max_link_id = max_basic_link_id
        else:
            max_link_id = max_other_link_id
        other_kg['links'] = find_self_links_method(other_kg, other_kg_link_propertes, max_link_id) #充实other_kg自身的links
    result_kg = {}
    result_kg['nodes'] = basic_kg['nodes'] + other_kg['nodes']
    if find_two_kg_links_method:
        result_kg['links'] = find_two_kg_links_method(basic_kg, other_kg, basic_kg_link_propertes, other_kg_link_propertes)
    else:
        result_kg['links'] = basic_kg['links'] + other_kg['links']
    if find_same_entities_method:
        need_2_fution_entities = find_same_entities_method(basic_kg, other_kg)
        if len(need_2_fution_entities):
            result_kg = entities_fution(result_kg, need_2_fution_entities)

    return result_kg

def find_self_links(kg, link_propertes, default_max_id): #完全查找知识库自身的链接，link_propertes为用于构建连接的属性
    exist_links = kg['links']
    if default_max_id:
        max_id = default_max_id
    else:
        if len(exist_links):
            max_id = int(sorted(exist_links, key=lambda link: int(link['id']), reverse=True)[0]['id']) + 1
        else:
            max_id = 0
    result_links = exist_links
    name_id_pair = [(entity['name'], int(entity['id'])) for entity in kg['nodes']]
    count = 0
    for entity in kg['nodes']:
         for property in entity.keys():
             if property in link_propertes: #是可以构造链接的属性
                for pair in name_id_pair:
                    if pair[0] != entity['name'] and pair[0] in entity[property]:
                        new_link = {"source":int(entity['id']), 'target':pair[1], 'name':property}
                        for exist_link in exist_links:
                            if exist_link['source']==new_link['source'] and exist_link['target'] == new_link['target'] and \
                                exist_link['name'] == new_link['name']:  #如果已经有此链接，则跳过
                                continue
                            else:
                                new_link['id'] = max_id
                                max_id += 1
                                count += 1
                                result_links.append(new_link)
    print('number of find self links is :', str(count))
    return result_links

def find_two_kg_links(basic_kg, other_kg, basic_kg_link_propertes, other_kg_link_propertes):
    '''
    找出两个知识库之间的交叉链接,其中，basic_kg_link_propertes是basic_kg用于构建链接的属性，other_kg_link_propertes是other_kg用于构建链接的属性
    :param basic_kg:
    :param other_kg:
    :param basic_kg_link_propertes:
    :param other_kg_link_propertes:
    :return:
    '''
    kg_preprocess(other_kg)
    if len(basic_kg['links']):
        max_basic_link_id = int(sorted(basic_kg['links'], key=lambda link: int(link['id']), reverse=True)[0]['id']) + 1
    else:
        max_basic_link_id = 0
    if len(other_kg['links']):
        max_other_link_id = int(sorted(other_kg['links'], key=lambda link: int(link['id']), reverse=True)[0]['id']) + 1
    else:
        max_other_link_id = 0
    if max_basic_link_id >= max_other_link_id:
        max_link_id = max_basic_link_id
    else:
        max_link_id = max_other_link_id
    result_links = basic_kg['links'] + other_kg['links']
    basic_kg_name_id_pair = [(entity['name'], int(entity['id'])) for entity in basic_kg['nodes']]
    ohter_kg_name_id_pair = [(entity['name'], int(entity['id'])) for entity in other_kg['nodes']]
    count = 0
    for entity in basic_kg['nodes']:
        for property in entity.keys():
            if property in basic_kg_link_propertes:  # 是可以构造链接的属性
                for pair in ohter_kg_name_id_pair:
                    if pair[0] != entity['name'] and pair[0] in entity[property]:
                        new_link = {"source": int(entity['id']), 'target': pair[1], 'name': property, 'id':max_link_id}
                        max_link_id += 1
                        count += 1
                        result_links.append(new_link)
    for entity in other_kg['nodes']:
        for property in entity.keys():
            if property in other_kg_link_propertes:  # 是可以构造链接的属性
                for pair in basic_kg_name_id_pair:
                    if pair[0] != entity['name'] and pair[0] in entity[property]:
                        new_link = {"source": int(entity['id']), 'target': pair[1], 'name': property, 'id':max_link_id}
                        max_link_id += 1
                        count += 1
                        result_links.append(new_link)
    print('number of find 2 kgs links is :', str(count))
    return result_links




if __name__=="__main__":
    basic_kg = json.load(codecs.open('../resource/kg/new_nodes_links_6.json', 'r', encoding='utf-8'))
    # other_kg = json.load(codecs.open('../dataAnalysis/data_file/output/demo_mix.json', 'r', encoding='utf-8'))
    # other_kg = kg_preprocess(other_kg)
    # basic_kg_link_propertes = [u'服务对象', u'服务渠道', u'联名单位', u'卡片种类', u'服务范围']
    # other_kg_link_propertes = [u'收款账户', u'适用对象', u'适用客户', u'所属产品线', u'适用范围', u'开办分行', u'预约取号',
    #                            u'签约他行账户', u'所属业务领域']
    # result_kg = other_kg_add_into_basic_kg(basic_kg, other_kg, basic_kg_link_propertes, other_kg_link_propertes, find_same_name_entities_when_only_name)
    # entityAnalysis.basicInfo(result_kg)
    # with codecs.open('./data/new_nodes_links_6.json', 'w', encoding='utf-8') as wf:
    #     json.dump(result_kg, wf, ensure_ascii=False)
    # same_entityes = find_same_name_entities_when_only_name(basic_kg, other_kg)
    # print('number of need to fusion entity pair is:', str(len(same_entityes)))  #28
    # json.dump(same_entityes, codecs.open('./data/same_name_entities.json', 'w', encoding='utf-8'), ensure_ascii=False)
    # print(len(same_entityes))
    # for pair in same_entityes:
    #     print(pair)
    #     print(same_entityes[pair])
    other_kg = json.load(codecs.open('./data/processed_data.json', 'r', encoding='utf-8'))
    entityAnalysis.basicInfo(other_kg)
    result_kg = other_kg_add_into_basic_kg(basic_kg, other_kg, find_same_entities_method=find_same_name_entities_when_only_name)
    with codecs.open('./data/new_nodes_links_7.json', 'w', encoding='utf-8') as wf:
        json.dump(result_kg, wf, ensure_ascii=False)
    entityAnalysis.basicInfo(result_kg)