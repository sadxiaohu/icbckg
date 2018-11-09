# coding=utf-8

import codecs
import json
import icbckg.config as config
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# not_extract_attributes = [str(line.strip()) for line in open("../resource/attributeExtraction/not_extract_attributes", 'r').readlines()]
not_extract_attributes = config.not_extract_attributes
def create_bank_from_KB_file(KB_file_path, out_Bank_file_path='../resource/indexBank/index_bank.json', out_all_content_file_path='../resource/indexBank/allContent'):
    with codecs.open(KB_file_path, 'r', encoding='utf-8') as kbf:
        all_entities = json.load(kbf)['nodes']
    bank = {}
    all_content = ''
    for entity in all_entities:
        bank[entity['name']] = ''
        for key in entity.keys():
            if key not in not_extract_attributes:
                bank[entity['name']] = entity[key]
                all_content += entity[key].strip()
    # print(json.dumps(bank, ensure_ascii=False))
    # print(json.dumps(all_content, ensure_ascii=False))
    with codecs.open(out_all_content_file_path, 'w', encoding='utf-8') as cf:
        cf.write(all_content)
    # with codecs.open(out_Bank_file_path, 'w', encoding='utf-8') as bkf:
    #     json.dump(bkf, bank, ensure_ascii=False)

if __name__ == "__main__":
    KB_file_path = '../resource/kg/nodes_links_8.json'
    out_Bank_file_path = '../resource/indexBank/index_bank.json'
    out_all_content_file_path = '../resource/indexBank/allContent'
    create_bank_from_KB_file(KB_file_path, out_Bank_file_path, out_all_content_file_path)