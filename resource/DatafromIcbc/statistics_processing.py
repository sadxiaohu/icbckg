#coding=utf-8
#python3
import jieba.posseg as pseg
import json
import codecs
import time
import requests
from bs4 import BeautifulSoup
def spbaike(name):
    headers = {
        'Host': 'baike.baidu.com',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36',
    }
    #time.sleep(1)
    info = {}
    url = 'https://baike.baidu.com/item/'
    url = url+name
    wb_data = requests.get(url,headers=headers).content
    soup = BeautifulSoup(wb_data,'lxml')
    datalist1 = soup.select('div.basic-info.cmn-clearfix > dl > dt')  # infoboxAttributes
    datalist2 = soup.select('div.basic-info.cmn-clearfix > dl > dd')  # infoboxAttributesValue
    description = soup.select('body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.lemma-summary > div ')
    if len(datalist1) != 0 and len(datalist2) != 0 :
        if len(description) != 0:
            description_ = ''
            for des in description:
                description_ += des.get_text()
            info['description'] = description_.replace('\n','').replace('\xa0','')
        taglist_ = soup.select('.taglist')
        taglist = ''
        for tag in taglist_:
            taglist += tag.get_text().replace('\n','')+','
        taglist = taglist[:-1]
        for i in range(len(datalist1)):
            info[datalist1[i].get_text().replace('\xa0','')] = datalist2[i].get_text().strip()
        info['taglist'] = taglist
        datalist3 = soup.select('.title-text')  # 详细信息
        if len(datalist3) != 0:
            detail_header = []
            detail_content = ''
            for data in datalist3:
                detail_header.append(data.get_text())
            detail_header.append('词条标签')
            datalist4 = soup.select('body > div.body-wrapper > div.content-wrapper > div > div.main-content > div ')
            for data in datalist4:
                detail_content += data.get_text()
            detail_content = detail_content.replace('\n','').replace('\xa0','').replace('编辑','')
            length = len(detail_header)
            for i in range(0,length-1):
                begin = detail_content.find(detail_header[i])
                end = detail_content.find(detail_header[i+1])
                info[detail_header[i].replace(name,'')] = detail_content[begin+len(detail_header[i]):end]
        return info
    else:
        url = 'https://baike.baidu.com/search/none?word='+name
        wb_data = requests.get(url,headers=headers).content
        soup = BeautifulSoup(wb_data,'lxml')
        if len(soup.select('.result-title')) > 0:
            msuit = soup.select('.result-title')[0].get_text().replace('_百度百科','')
            if fuzzy_match(msuit,name):
                url = 'https://baike.baidu.com/item/'+msuit
                wb_data = requests.get(url,headers=headers).content
                soup = BeautifulSoup(wb_data,'lxml')
                datalist1 = soup.select('div.basic-info.cmn-clearfix > dl > dt')
                datalist2 = soup.select('div.basic-info.cmn-clearfix > dl > dd')
                description = soup.select('body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.lemma-summary > div')
                if len(description) != 0:
                    description_ = ''
                    for des in description:
                        description_ += des.get_text()
                        info['description'] = description_.replace('\n','').replace('\xa0','')
                taglist_ = soup.select('.taglist')
                taglist = ''
                for tag in taglist_:
                    taglist += tag.get_text().replace('\n','')+','
                taglist = taglist[:-1]
                for i in range(len(datalist1)):
                    info[datalist1[i].get_text().replace('\xa0','')] = datalist2[i].get_text().strip()
                info['name_baike'] = msuit
                info['taglist'] = taglist
                return info
            else:
                info = 0
                # print("查询不到此单位，请修改名称后重新查询：",name)
                return info
        else:
            # print("查询不到此单位，请修改名称后重新查询：",name)
            info = 0
            return info
# 数据预处理
def pre_process(data):
    origin_nodes = data['nodes']
    origin_links = data['links']
    delete_no_node = []
    new_nodes = []
    new_links = []
    # punctuation = [',','.','.',':','!','?','，']
    # 删除重复的关系
    delete_no_link = []
    links_length = len(origin_links)
    for i in range(links_length):
        for j in range(i+1,links_length):
            if (origin_links[i]['source'] == origin_links[j]['source']) and (origin_links[i]['target'] == origin_links[j]['target']) and (origin_links[i]['name'] == origin_links[j]['name']):
                print("重复结点",origin_links[i]['id'],origin_links[j]['id'])
                delete_no_link.append(origin_links[j]['id'])
    # 筛掉节点名称为标点符号，空，或单个字符的结点，同时删除有包含有该节点的关系
    for node in origin_nodes:
        if len(node['name']) <= 1:
            # print(node['id'])
            delete_no_node.append(node['id'])
        else:
            new_nodes.append(node)
    for link in origin_links:
        if (link['source']  in delete_no_node ) or (link['target'] in delete_no_node) or (link['id'] in delete_no_link):
            print
        else:
            new_links.append(link)
    # 对节点id和关系id重新排序,id从2000开始
    new_node_id = 2000
    new_link_id = 3000
    old2new = {}  # 旧id到新id的映射
    source2target = {}  # 关系sourceid到关系targetid和关系名的映射
    for node in new_nodes:
        old_node_id = node['id']
        node['id'] = str(new_node_id)
        old2new[old_node_id] = new_node_id
        new_node_id += 1
    for link in new_links:
        link['id'] = new_link_id
        link['source'] = old2new[link['source']]
        link['target'] = old2new[link['target']]
        if link['source'] not in source2target:
            source2target[link['source']] = []
        source2target[link['source']].append({link['target']:link['name']})
        new_link_id += 1
    id2name = {}  # 结点id到结点name的映射
    for node in new_nodes:
        id = int(node['id'])
        name = node['name']
        id2name[id] = name
    # 将结点包含的关系填充到该节点内，以扩充结点
    for node in new_nodes:
        source_id = int(node['id'])
        if source_id in source2target:
            for target in source2target[source_id]:
                for target_id in target:
                    target_name = id2name[target_id]
                    link_name = target[target_id]
                if link_name not in node:
                    node[link_name] = target_name
                else:
                    node[link_name] += '，'+target_name
    new_data = {'nodes':new_nodes,"links":new_links}
    return new_data
# 用莱文斯坦距离（编辑距离）计算原始结点名与新结点名的相似度，不小于于0.6返回True，否则返回False
def fuzzy_match(original_name,new_name):
    threshold = 0.6
    if (original_name in new_name) or (new_name in original_name):
        score = min(float(len(original_name))/len(new_name),float(len(new_name))/len(original_name))
        if score >= 0.2:
           return True
    else:
        score = levenshtein(original_name,new_name)
        if score >= threshold:
            return True
        else:
            return False
#动态规划实现莱文斯坦距离
def levenshtein(string1,string2):
    if len(string1) > len(string2):
        string1,string2 = string2,string1
    if len(string1) == 0:
        return len(string2)
    if len(string2) == 0:
        return len(string1)
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
    return round(1-distance_matrix[str1_length-1][str2_length-1]/max(len(string1),len(string2)),2)

if __name__=='__main__':
    data_path = "./icbcdata/demo_structuredData.json"
    with codecs.open(data_path,'r',encoding='utf-8') as foo:
        data = json.load(foo)
    new_data = pre_process(data)
    nodes = new_data['nodes']
    links = new_data['links']
    for node in nodes:
        info = spbaike(node['name'])
        if info != 0:  # info为0意无法从百度百科查询相关节点信息
            for key in info:
                if key not in node:
                    node[key] = info[key]
                else:
                    node[key] = '，'+info[key]
    json_data = json.dumps({'nodes':nodes,"links":links},ensure_ascii=False)
    with codecs.open('./icbcdata/processed_data.json','w',encoding='utf-8') as foo:
        foo.write(json_data)

    # print(detail_content)
    # print(datalist2)
    #print(spbaike(name))
    # print(new_data)
    # print(levenshtein('代理保险业务','代理村售保险业务'))
'''
body > div.body-wrapper > div.content-wrapper > div > div.main-content > div:nth-child(12) > h2
body > div.body-wrapper > div.content-wrapper > div > div.main-content > div:nth-child(22)
body > div.body-wrapper > div.content-wrapper > div > div.main-content > div:nth-child(13)
body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.lemma-summary
body > div.body-wrapper > div.content-wrapper > div > div.main-content > div.basic-info.cmn-clearfix > dl.basicInfo-block.basicInfo-right > dt:nth-child(1)
'''


