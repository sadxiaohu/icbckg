# -*- coding: utf-8 -*-
import configInfo
import codecs
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

basic_kg = json.load(codecs.open(configInfo.bank_file_path, 'r', encoding='utf-8'))

def basicInfo(kg):
    if 'nodes' in kg.keys():
        all_entities = kg['nodes']  # list, item:dict
        print("nodes total number:", len(all_entities))
        same_name_entities = []
        for entity in all_entities:
            for inner_entity in all_entities:
                if entity['name'] == inner_entity['name'] and entity['id'] != inner_entity['id']:
                    same_name_entities.append(entity['name'])
        if len(same_name_entities) > 0:
            print('there are same name entities, they are :', same_name_entities)
        else:
            print('there are not same name entities.')

    else:
        print("kg has not 'nodes' element!")

    if 'links' in kg.keys():
        all_links = kg['links'] #list, item:dict
        print("links total number:", len(all_links))
    else:
        print("kg has not 'links' element!")

def who_has_not_taglist():
    bank_path = configInfo.bank_file_path
    all_entities = json.load(codecs.open(bank_path, 'r', encoding='utf-8'))['nodes']
    for entity in all_entities:
        if 'taglist' not in entity.keys():
            print(entity['name'])

def icbc_provide_demo_analysis():  #两个图谱数据文件分析及融合
    file_semiStructure_path = './data_file/demo_semiStructure.json'
    file_yaowen_path = './data_file/demo_yaowen.json'

    mix_out_file = './data_file/output/demo_mix.json'

    with codecs.open(file_semiStructure_path, 'r', encoding='utf-8') as srf:
        kg_semi = json.load(srf, encoding='utf-8')
        basicInfo(kg_semi)

        with codecs.open(file_yaowen_path, 'r', encoding='utf-8') as yrf:
            kg_yaowen = json.load(yrf, encoding='utf-8')
            basicInfo(kg_yaowen)

            common_entites = [entity['name'] for entity in kg_semi['nodes'] if entity['name'] in
                                [inner_entity['name'] for inner_entity in kg_yaowen['nodes']]]
            print('len of common entites:', len(common_entites)) #有4个同名实体
            print('common_entites are', common_entites)
            print('common_entites are', [entity.encode('gb2312') for entity in common_entites]) #u'外汇买卖', u'理财产品', u'结售汇', u'账户贵金属'

            #融合为一个文件
            basic_nodes = kg_semi['nodes']
            for entity in kg_yaowen['nodes']:
                if entity['name'] not in common_entites:
                    basic_nodes.append(entity)
                else:
                    for entity_semi in basic_nodes:
                        if entity_semi['name'] == entity['name']:
                            for property_name in entity.keys():
                                if property_name not in entity_semi.keys():
                                    entity_semi[property_name] = entity[property_name]
            mixed_kg = {'nodes':basic_nodes, 'links':[]}
            with codecs.open(mix_out_file, 'w', encoding='utf-8') as wf:
                json.dump(mixed_kg, wf, ensure_ascii=False)


if __name__=="__main__":
    basicInfo(basic_kg)
    mix_demo_kg = json.load(codecs.open('./data_file/output/demo_mix.json', 'r', encoding='utf-8'))
    basicInfo(mix_demo_kg)