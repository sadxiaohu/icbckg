#coding=utf-8
#python3
import codecs
import json
import xlrd
# 判断是否有最佳答案，如果有则返回最佳答案，否则返回False
def is_best_answer(answerlist):
    for answer in answerlist:
        if answer[2] == '是':
            return answer
    return False
#在无最佳答案的情况下，挑选出获赞数最高的答案
def most_support_answer(answerlist):
    new_answer_list = sorted(answerlist,key = lambda x:x[3],reverse = True)
    if new_answer_list[0][3] > 0:
        return new_answer_list[0]
    else:
        return False
if __name__=='__main__':
    path = './icbcdata/question_collect.xls'
    sheetno = 1
    question_col = 0
    detail_col = 1
    answer_col = 5
    best_answer_col = 7
    support_col = 8
    question_id = 0
    question_dict = {}
    data = {}
    nodes = []
    excel_data = xlrd.open_workbook(path)
    table = excel_data.sheets()[sheetno]
    nrows = table.nrows
    for row in range(1,nrows):
        question = table.row_values(row)[question_col]
        detail = table.row_values(row)[detail_col]
        answer = table.row_values(row)[answer_col]
        best_answer = table.row_values(row)[best_answer_col]
        support = int(table.row_values(row)[support_col])
        # print(question)
        if question not in question_dict:
            question_dict[question] = []
        question_dict[question].append([detail,answer,best_answer,support])
    for question in question_dict:
        node = {}
        unknown_answer = is_best_answer(question_dict[question])
        if unknown_answer is not False:
            answer = unknown_answer
        else:
            answer = most_support_answer(question_dict[question])
        if answer is False:
            continue
        node['question'] = question
        node['detail'] = answer[0]
        node['answer'] = answer[1]
        node['best_answer'] = answer[2]
        node['support'] = answer[3]
        node['id'] = question_id
        question_id += 1
        nodes.append(node)
    data['nodes'] = nodes
    json_data = json.dumps(data,ensure_ascii=False)
    with codecs.open('./icbcdata/question_2.json','w',encoding='utf-8') as foo:
        foo.write(json_data)