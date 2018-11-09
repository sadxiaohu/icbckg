#coding=utf-8
import requests
from bs4 import BeautifulSoup
import json
import codecs
def webNodesGet(word_url_dict):
    nodes = []
    id = 0
    for word in word_url_dict:
        url = 'http://www.icbc.com.cn'
        url = url+word_url_dict[word]
        wb_data = requests.get(url).content
        soup = BeautifulSoup(wb_data,'lxml')
        datalist1 = soup.select('.more')
        info = {}
        attr = []
        for data in datalist1 :
            attr.append(data.get_text().replace('\n',''))
            info[data.get_text().replace('\n','')]=''
        datalist2 = soup.select('table > tbody > tr > td ')
        if len(datalist1) != 0 and len(datalist2) != 0:
            string=''
            for i in range(2,len(datalist2)):
                string += datalist2[i].get_text().strip().replace(' ','')
            string = string.replace('\r','')
            string = string.replace('\n','')
            string = string.replace('\t','')
            string = string.replace('[返回页首]','')
            string = string.replace('\u3000','')
            length = len(attr)
            for i in range(0,length-1):
                begin = string.find(attr[i])
                end = string.find(attr[i+1])
                info[attr[i]] = string[begin+len(attr[i]):end]
            info[attr[-1]] = string[(string.find(attr[-1]))+len(attr[-1]):]
            info['name'] = word
            info['id'] = str(id)
            #print(info)
            nodes.append(info)
            id += 1
    josn_data = json.dumps({"nodes":nodes},ensure_ascii=False)
    with codecs.open('nodesfromweb.json','w',encoding='utf-8') as foo:
        foo.write(josn_data)
    #print(id)

#个人网上银行部分信息
url1 = 'http://www.icbc.com.cn/ICBC/电子银行/电子银行产品/金融a家产品/个人网上银行/个人网上银行/'
wb_data = requests.get(url1).content
soup = BeautifulSoup(wb_data,'lxml')
datalist1 = soup.select('li > ul > li > ul > li > a')
datalist2 = soup.select('li > ul > li > a')
datalist1.extend(datalist2)
#企业网上银行部分信息
url2 = 'http://www.icbc.com.cn/ICBC/电子银行/企业电子银行产品/工行财e通产品/企业网上银行/'
wb_data = requests.get(url2).content
soup = BeautifulSoup(wb_data,'lxml')
datalist3 = soup.select('li > ul > li > ul > li > a')
datalist4 = soup.select('li > ul > li > a')
datalist3.extend(datalist4)
datalist1.extend(datalist3)
entity = {}
for data in datalist1:
    if data.get('href') != None:
       entity[data.get_text().replace(' >','')] = data['href']
webNodesGet(entity)
