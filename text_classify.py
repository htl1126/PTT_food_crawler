#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import jieba
import page_crawler
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from BeautifulSoup import BeautifulSoup

# ref: http://xiaosu.blog.51cto.com/2914416/1340932
reload(sys)
sys.setdefaultencoding('utf8')

class text_classifier(object):
    def __init__(self):
        # labels: (1) 火鍋 (2) 中式 (3) 西式 (4) 日韓 (5) 吃到飽 (6) 東南亞
        self.keyword_dict = {u'火鍋': [u'鍋', u'涮'],
                             u'中式': [u'牛肉麵', u'雞排', u'便當', u'鍋貼', u'炒麵', u'炒飯',
                                       u'燴飯', u'羹', u'米糕', u'割包', u'刈包', u'豆漿', u'蛋餅',
                                       u'豆花', u'麵線', u'貴州', u'黔', u'廣東', u'粵', u'福建',
                                       u'閩', u'浙江', u'浙', u'上海', u'山東', u'魯', u'東北',
                                       u'新疆', u'疆', u'蒙古', u'蒙', u'四川', u'川', u'湖南',
                                       u'湘', u'小籠', u'湯包', u'包子', u'魚翅', u'湯圓', u'菜飯',
                                       u'雲南', u'滇', u'緬', u'半筋', u'鹽酥', u'鹹酥'],
                             u'西式': [u'咖啡', u'早午餐', u'brunch', u'Brunch', u'帕尼尼',
                                       u'鬆餅', u'義大利麵', u'漢堡', u'三明治', u'海鮮飯',
                                       u'燉飯', u'薯條', u'吐司', u'乾式熟成', u'筆管麵'],
                             u'日韓': [u'拉麵', u'丼', u'韓式泡菜', u'日式', u'韓式', u'壽司',
                                       u'生魚片', u'天婦羅', u'蓋飯', u'親子丼', u'燒肉', u'定食'],
                             u'吃到飽': [u'Buffet', u'buffet', u'自助餐', u'吃到飽'],
                             u'東南亞': [u'河粉', u'越式', u'泰式', u'清真', u'月亮蝦餅',
                                         u'椒麻雞']}
        self.keyword_boundary = []
        self.feature_set = []
        self.update_dict()

    def update_dict(self):
        for category in self.keyword_dict:
            for word in self.keyword_dict[category]:
                jieba.add_word(word)

    def text_cut(self, text):
        term_dict = {}
        for category in self.keyword_dict:
            for term in self.keyword_dict[category]:
                term_dict[term] = 0
        seg_list = jieba.cut(text)
        for item in seg_list:
            if item in term_dict:
                term_dict[item] += 1
        return term_dict

    def gen_feature(self, file_name, train_set_size):
        pass

    def update_feature(self, file_name, mode):
        crawler = page_crawler.ptt_crawler()
        classifier = text_classifier()
        buf = ''
        i = 0
        total = 0
        with open(file_name, 'r') as f:
            for line in f:
                line = line.strip()
                total += 1
                if mode == 'train':
                    url, label, _ = line.split(';')
                elif mode == 'test':
                    url, _ = line.split(';')
                try:
                    page_data = BeautifulSoup(crawler.get_page(url))
                except:
                    continue
                raw_text = page_data.text.split('\n')
                final_text = ''
                for text in raw_text:
                    final_text = '{0}{1}'.format(final_text, text)
                    if u'發信站: 批踢踢實業坊' in text:
                        break
                term_freq = classifier.text_cut(final_text)
                if mode == 'train':
                    buf = '{0}{1} ; {2}; '.format(buf, url, label)
                elif mode == 'test':
                    buf = '{0}{1}; '.format(buf, url)
                buf = '{0}{1}\n'.format(buf, ','.join([str(term_freq[term]) for term in term_freq]))
                i += 1
        with open(file_name, 'w') as f:
            f.write(buf)
        print "{0}/{1} instances updated.".format(i, total)

    def read_feature(self, file_name):
        with open(file_name) as f:
            for line in f:
                line = line.strip()
                url, label, feature = line.split(';')
                self.feature_set.append({'url': url, 'label': label, 'feature':
                                    [int(item) for item in feature.split(',')]})

def main(input_file, train_data_file):
    crawler = page_crawler.ptt_crawler()
    classifier = text_classifier()
    classifier.update_feature(train_data_file, 'test')

if __name__ == '__main__':
	main(sys.argv[1], sys.argv[2])
