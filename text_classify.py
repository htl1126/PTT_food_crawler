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
                                       u'雲南', u'滇', u'緬', u'半筋', u'鹽酥', u'鹹酥', u'口水雞',
                                       u'銀絲捲', u'宮保', u'滷肉飯', u'空心菜', u'爌肉', u'菜頭',
                                       u'白菜滷', u'薑母鴨'],
                             u'西式': [u'咖啡', u'早午餐', u'brunch', u'Brunch', u'帕尼尼',
                                       u'鬆餅', u'義大利麵', u'漢堡', u'三明治', u'海鮮飯',
                                       u'燉飯', u'薯條', u'吐司', u'乾式熟成', u'筆管麵', u'法國',
                                       u'布蕾', u'布丁', u'蛋糕', u'餅乾', u'蒙布朗', u'漢堡排'],
                             u'日韓': [u'拉麵', u'丼', u'韓式泡菜', u'日式', u'韓式', u'壽司',
                                       u'生魚片', u'天婦羅', u'蓋飯', u'親子丼', u'燒肉', u'定食',
                                       u'章魚燒', u'石鍋', u'韓國', u'豆腐煲', u'部隊鍋',
                                       u'銅盤烤肉', u'五花肉', u'壽喜燒', u'唐揚', u'烏龍麵',
                                       u'蓋飯'],
                             u'吃到飽': [u'Buffet', u'buffet', u'吃到飽'],
                             u'東南亞': [u'河粉', u'越式', u'泰式', u'清真', u'月亮蝦餅',
                                         u'椒麻雞', u'印度', u'中東', u'土耳其']}
        self.label_text = {'1': u'火鍋', '2': u'中式', '3': u'西式', '4': u'日韓', '5': u'吃到飽',
                           '6': u'東南亞'}
        self.keyword_boundary = []
        self.feature_set = []
        self.update_dict()
        self.crawler = page_crawler.ptt_crawler()
        self.clf = MultinomialNB()

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

    def gen_feature(self, file_name, train_set_size=10000000):
        buf = ''
        with open(file_name, 'r') as f:
            for line in f:
                #buf = '{0}{1}'.format(buf, line)
                print line.strip()
                if line.startswith('url'):
                    line = line.strip()
                    url = line.split(' ')[1]
                    try:
                        page_data = BeautifulSoup(self.crawler.get_page(url))
                    except:
                        continue
                    raw_text = page_data.text.split('\n')
                    final_text = ''
                    for text in raw_text:
                        final_text = '{0}{1}'.format(final_text, text)
                        if u'發信站: 批踢踢實業坊' in text:
                            break
                    term_freq = self.text_cut(final_text)
                    feature = [[term_freq[term] for term in term_freq]]
                    result = str(self.clf.predict(feature)[0])
                if line.startswith('address'):
                    #buf = buf.strip()
                    #buf = '{0}\ncategory {1}\n'.format(buf, self.label_text[result])
                    print 'category {0}'.format(self.label_text[result])
        #with open(file_name, 'w') as f:
        #    f.write(buf)

    def update_feature(self, file_name, mode):
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
                    page_data = BeautifulSoup(self.crawler.get_page(url))
                except:
                    continue
                raw_text = page_data.text.split('\n')
                final_text = ''
                for text in raw_text:
                    final_text = '{0}{1}'.format(final_text, text)
                    if u'發信站: 批踢踢實業坊' in text:
                        break
                term_freq = self.text_cut(final_text)
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

    def train(self, train_data_file):
        feature = []
        label = []
        with open(train_data_file, 'r') as f:
            for line in f:
                line = line.strip()
                _, one_label, one_feature = line.split(';')
                label.append(int(one_label))
                one_feature = [int(item) for item in one_feature.split(',')]
                feature.append(one_feature)
        feature = np.array(feature)
        label = np.array(label)
        self.clf.fit(feature, label)
        print 'Finished training with file \'{0}\''.format(train_data_file)

def main():
    crawler = page_crawler.ptt_crawler()
    classifier = text_classifier()
    classifier.train('train_data')
    #classifier.update_feature('train_data', 'train')
    classifier.gen_feature('food_ptt_imgpos_tw_full')

if __name__ == '__main__':
	main()
