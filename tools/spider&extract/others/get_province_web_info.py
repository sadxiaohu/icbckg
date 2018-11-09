# -*- coding: UTF-8 -*-
'''
author:lxf
env:python2
用途：爬取工商银行各分行的数据
使用工具：URLlib2
解析架构：beautifulsoup
遗留问题：
1）异常省份过滤失效
2）Email检索失效
'''
#import icbckg.config as config
#from graph import owlNeo4j
import requests
import urllib2
import re
from bs4 import BeautifulSoup
import json
import codecs
import  sys
print  sys.maxunicode

if __name__ == '__main__':
    web_url=''
    #spider_urls_path = config.spider_urls_path
    spider_urls_path = './resource_urls.json'
    with codecs.open(spider_urls_path, 'r', encoding='utf-8') as rf:
        web_url = json.load(rf)['all_organization']

    nodes = []
    links = []
    # new_node_id = owlNeo4j.get_max_id_in_nodes()+1
    # new_link_id = owlNeo4j.get_max_id_in_links()+1
    new_node_id = 1196
    new_link_id = 981
    wb_data = urllib2.urlopen(web_url)
    soup = BeautifulSoup(wb_data, "lxml", from_encoding="utf-8")
    provinces_table = soup.find_all('a', target='_blank', text=re.compile(u'.*分行网站'))
    with codecs.open('./exception_province_bank', 'r', encoding='utf-8') as erf:
        exception_banks = [bank.strip() for bank in erf.readlines()[1:]] #格式不同的几个网站
    for link in provinces_table:
        try:
            if link.get_text().encode('utf-8') not in exception_banks:  #普通分行网站格式
                #print link.name, link['href'], link.get_text()
                sub_bank_data = urllib2.urlopen(link['href'])
                sub_bank_soup = BeautifulSoup(sub_bank_data, "lxml", from_encoding="utf-8")
                description = u''
                for p in sub_bank_soup('p', text=re.compile(u'.*[^分行经营综述]$')):
                    description += p.get_text().strip()
                    description += '\n'
                main_node = {'id':new_node_id,  #分行主节点
                             'name':link.text[:-2],
                             'taglist':u"分行",
                             "category":u"分行",
                             u"经营综述":description,
                             u"地址":(sub_bank_soup.find(['div','td'], text=re.compile(u'地址')).string.strip()[3:] if sub_bank_soup.find(['div','td'], text=re.compile(u'地址')) else u''),
                             u"电话":(sub_bank_soup.find(['div','td'], text=re.compile(u'电话')).string.strip()[3:] if sub_bank_soup.find(['div','td'], text=re.compile(u'电话')) else u''),
                             u"邮编":(sub_bank_soup.find(['div','td'], text=re.compile(u'邮编')).string.strip()[3:] if sub_bank_soup.find(['div','td'], text=re.compile(u'邮编')) else u''),
                             u"E-mail":(sub_bank_soup.find(['div','td'], text=re.compile(u'E-mail')).a.string.strip()[3:] if sub_bank_soup.find(['div','td'], text=re.compile('E-mail')) else u'')}
                nodes.append(main_node)
                new_node_id += 1
                #特色业务
                feature_business_url = sub_bank_soup.find('a', text=u'特色业务')['href']
                feature_business_data = urllib2.urlopen(feature_business_url)
                feature_business_soup = BeautifulSoup(feature_business_data, "lxml", from_encoding="utf-8")

        except Exception as e:
            print(link.get_text())
            print(e)


    # print(nodes)
    with codecs.open('./result.json', 'w', encoding='utf-8') as wf:
        json.dump(nodes, wf, ensure_ascii=False)