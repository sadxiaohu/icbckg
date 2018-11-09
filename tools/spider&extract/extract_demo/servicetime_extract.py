#coding=utf-8
import json
import codecs
import re
defaultpath = './'


if __name__=='__main__':
    with codecs.open(defaultpath+r'\new_nodes_2.json','r',encoding='utf-8') as foo:  # 打开待处理数据集，文件名根据实际情况填写
        data = json.load(foo)
    links = []
    idcount = 0
    newnodes = []
    timedict = [u'7X24',u'7x24',u'7*24']
    newnodes = []
    timedict = [u'7X24',u'7x24',u'7*24',u'7×24']
    attr1 = u'服务渠道与时间'
    attr2 = u'服务时间'
    count = 0
    pattern1 = r"[周|星期][一二三四五六日][~|至|到|-][周|星期][一二三四五六日]\d*[:|：]?\d*[-|－|到|至|~]?\d*[:|：]?\d*"  # 根据正则表达式抽取服务时间
    for entity1 in data['nodes']:#从服务渠道与时间中提取时间
        if int(entity1['id']) >=246000:
            if attr1 in entity1:
                  print 'OK'
                  entity1[attr2] = ''
                  flag = 0
                  for key in timedict:
                      if key in entity1[attr1]:
                          flag = 1
                          entity1[attr2] = "7*24小时全天候"
                          break
                  if flag == 0:
                      it = re.finditer(pattern1,entity1[attr1])
                      for match in it:
                          entity1[attr2] += match.group()
                      if entity1[attr2] != '':
                          count += 1
                  newnodes.append(entity1)
            else:
                newnodes.append(entity1)
    json_data = json.dumps({'nodes':newnodes})
    with codecs.open("new_nodes_3.json",'w',encoding='utf-8') as foo:
        foo.write(json_data)

