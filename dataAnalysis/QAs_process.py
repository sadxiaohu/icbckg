# coding=utf-8
# author:lxf'

import codecs
import json

if __name__=='__main__':
    QAs_corpus_path = '../resource/questionsAndAnswers/question_types.json'
    result_path = './data_file/output/questions_ui_table'

    with codecs.open(QAs_corpus_path, 'r', encoding='utf-8') as rf:
        with codecs.open(result_path, 'w', encoding='utf-8') as wf:
            questions_list = json.load(rf, encoding='utf-8')
            for each_list in questions_list:
                questions = each_list['question_list']
                for question in questions:
                    wf.write('<a href="#" class="sampleQuestionItem">'+question+'</a><br>')
                    wf.write('\n')