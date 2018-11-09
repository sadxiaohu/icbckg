#coding=utf-8
#文件用途：web爬虫，爬取网页内容
#注意：环境为python3
#author:lixufeng

'''
import requests
from bs4 import BeautifulSoup
import json
import codecs
import  re
from urllib.parse import unquote
import time

def webNodesGet(word_url_dict):
    nodes = []
    id = 229
    pattern= re.compile(r'(\w+)')
    for word in word_url_dict:
        url = 'http://www.icbc.com.cn'
        url = url+word_url_dict[word]
        try:
            wb_data = requests.get(url).content
            soup = BeautifulSoup(wb_data,'lxml')
            datalist1 = soup.select('#MyFreeTemplateUserControl > p > strong ')
            info = {}
            attr = []
            for data in datalist1 :2
                attr.append(data.get_text().replace('\n','').replace('\t','').replace('\r','').replace(' ',''))
                #info[data.get_text().replace('\n','')]=''
            datalist2 = soup.select('#MyFreeTemplateUserControl > p ')
            # print(datalist1)
            #print(attr)
            #print(datalist2)
            if len(datalist1) != 0 and len(datalist2) != 0:
                string=''
                for i in range(0,len(datalist2)):
                    string += datalist2[i].get_text().strip().replace(' ','')
                string = string.replace('\r','')
                string = string.replace('\n','')
                string = string.replace('\t','')
                string = string.replace('[返回页首]','')
                string = string.replace('\u3000','')
                #print(string)
                length = len(attr)
                for i in range(0,length-1):
                    begin = string.find(attr[i])
                    end = string.find(attr[i+1])
                    if string[begin+len(attr[i]):end] != '':
                      info[re.sub(r'[一二三四五六七八九十1234567890☆、()]','',attr[i]).strip()] = string[begin+len(attr[i]):end]
                if string[(string.find(attr[-1]))+len(attr[-1]):] !='':
                    info[re.sub(r'[一二三四五六七八九十1234567890☆、()]','',attr[-1]).strip()] = string[(string.find(attr[-1]))+len(attr[-1]):]
                taglist = pattern.findall(word_url_dict[word])
                tagstring = ''
                for i in range(1,len(taglist)-1):
                   if i != len(taglist)-2:
                       tagstring = tagstring+taglist[i]+','
                   else :
                       tagstring = tagstring+taglist[i]

                info['name'] = word.replace('>','').strip()
                info['id'] = str(id)
                info['taglist'] = tagstring
                nodes.append(info)
                id += 1
        except:
            print(word)
    print(len(nodes))
    josn_data = json.dumps({"nodes":nodes},ensure_ascii=False)
    with codecs.open('investment-2.json','w',encoding='utf-8') as foo:
        foo.write(josn_data)
    #print(id)
def webNodesGet2(word_url_dict):#提取信用卡infobox
    nodes = []
    id = 281
    pattern= re.compile(r'(\w+)')
    for word in word_url_dict:
        url = 'http://www.icbc.com.cn'
        url = url+word_url_dict[word]
        try :
            wb_data = requests.get(url).content
            soup = BeautifulSoup(wb_data,'lxml')
            datalist1 = soup.select('tr > td > div > strong')
            datalist2 = soup.select('#MyFreeTemplateUserControl > p ')
            datalist3 = []
            if (len(datalist1)*2) == len(datalist2) and len(datalist2) > 0 :
                for i in range(1,len(datalist2),2):
                    datalist3.append(datalist2[i].get_text().replace('\n',''))
                info = {}
                for i in range(len(datalist1)):
                    info[datalist1[i].get_text()] = datalist3[i]
                taglist = pattern.findall(word_url_dict[word])
                tagstring = ''
                for i in range(1,len(taglist)-2):
                   if i != len(taglist)-3:
                       tagstring = tagstring+taglist[i]+','
                   else :
                       tagstring = tagstring+taglist[i]
                info['name'] = word
                info['id'] = str(id)
                info['taglist'] = tagstring
                id += 1
                nodes.append(info)
        except:
            print(word)
    josn_data = json.dumps({"nodes":nodes},ensure_ascii=False)
    with codecs.open('creditcard-2.json','w',encoding='utf-8') as foo:
        foo.write(josn_data)



# #个人网上银行部分信息
# url1 = 'http://www.icbc.com.cn/ICBC/%E7%89%A1%E4%B8%B9%E5%8D%A1/%E5%8D%A1%E7%89%87%E4%B8%96%E7%95%8C/%E8%81%94%E5%90%8D%E5%8D%A1%E4%BA%A7%E5%93%81%E7%B3%BB%E5%88%97/%E5%8C%BA%E5%9F%9F%E8%81%94%E5%90%8D%E8%AE%A4%E5%90%8C%E5%8D%A1/'
# wb_data = requests.get(url1).content
# soup = BeautifulSoup(wb_data,'lxml')
# datalist1 = soup.select(' tr > td > div > a')
# datalist2 = soup.select(' tr > td > p > a')
# datalist3 = soup.select('tr > td > a ')
# datalist4 = soup.select(' span  > a')
# datalist1.extend(datalist2)
# datalist1.extend(datalist3)
# datalist1.extend(datalist4)
# print(len(datalist1))
# entity = {}
# for data in datalist1:
#     if data.get('href') != None:
#        entity[data.get_text().replace(' >','')] = unquote(data['href'])
# print(entity)
# webNodesGet2(entity)

#企业网上银行部分信息
url2 = 'http://www.icbc.com.cn/ICBC/%E9%87%91%E8%9E%8D%E5%B8%82%E5%9C%BA%E4%B8%93%E5%8C%BA/%E4%BA%A7%E5%93%81%E6%9C%8D%E5%8A%A1/%E4%B8%AA%E4%BA%BA%E4%BA%A7%E5%93%81/%E6%8A%95%E8%B5%84%E4%BA%A4%E6%98%93%E7%B1%BB/%E8%B4%A6%E6%88%B7%E5%9F%BA%E6%9C%AC%E9%87%91%E5%B1%9E/'
wb_data = requests.get(url2).content
soup = BeautifulSoup(wb_data,'lxml')
datalist3 = soup.select('div > div > ul > li > a')
datalist4 = soup.select('li > ul > li > a')
datalist3.extend(datalist4)
# datalist1.extend(datalist3)
#print(datalist3)
entity = {}
for data in datalist3:
    if data.get('href') != None:
       entity[data.get_text().replace(' >','')] = unquote(data['href'].replace('\r','').replace('\n',''))
print(len(entity),entity)
webNodesGet(entity)
'''
'''
#MyFreeTemplateUserControl
#SecChannelNav > li:nth-child(1) > a
#SecChannelNav > li.show
#SecChannelNav > li.show#abc1669783058 > li:nth-child(1) > a
#abc1669783058 > li:nth-child(2) > a
#abc1669783058 > li:nth-child(1)
#SecChannelNav > li:nth-child(2)
#abc720862453 > li:nth-child(1) > a
http://www.icbc.com.cn/ICBC/电子银行/电子银行产品/金融a家产品/融e行网上银行/个人网上银行/
#MyFreeTemplateUserControl > table:nth-child(4) > tbody > tr > td > p:nth-child(1) > strong
http://www.icbc.com.cn/ICBC/%E5%85%AC%E5%8F%B8%E4%B8%9A%E5%8A%A1/%E4%BC%81%E4%B8%9A%E6%9C%8D%E5%8A%A1/%E7%BB%93%E7%AE%97%E6%9C%8D%E5%8A%A1/%E7%8E%B0%E9%87%91%E7%AE%A1%E7%90%86/%E5%9B%BD%E5%86%85%E7%BB%93%E7%AE%97%E4%B8%9A%E5%8A%A1/%E8%B4%A6%E6%88%B7%E7%AE%A1%E7%90%86/
#detailCon > div > div.MsgBox > div > div:nth-child(1) > div > ul > li > a
'''