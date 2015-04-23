#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import codecs
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen, build_opener

# ref: http://stackoverflow.com/questions/4545661/unicodedecodeerror
#      -when-redirecting-to-file
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

class ptt_crawler(object):

    def remove_colon(self, s):
        if ':' in s:
            s = s.split(':')[-1]
            if u'：' in s:
                s = s.split(u'：')[-1]
        elif u'：' in s:
            s = s.split(u'：')[-1]
        return s

    def get_page(self, url):
        try:
            data = urlopen(url)
            return data
        # ref: http://stackoverflow.com/questions/9265616/why-does-this-url-raise-badstatusline
        #      -with-httplib2-and-urllib2
        except:
            opener = build_opener()
            headers = {'User-Agent': ('Mozilla/5.0 (Windows NT 5.1;'
                                    ' rv:10.0.1) Gecko/20100101 Firefox/10.0.1')}
            opener.addheaders = headers.items()
            response = opener.open(url)
            return response.read()

    def get_title_list(self, data):
        title_lst = data.findAll('div', {'class': 'title'})
        return title_lst

    def extract_store_info(self, data, store_info):
        for line in data:
            if ((u'址：' in line or u'址:' in line or u'點：' in line or u'點：' in line)
                and u'網址' not in line):
                line = self.remove_colon(line.lstrip()).lstrip()
                store_info['address'] = line
            elif u'話：' in line or u'話:' in line:
                line = self.remove_colon(line.lstrip()).lstrip()
                store_info['phone'] = line
            elif u'稱：' in line or u'稱:' in line:
                line = self.remove_colon(line.lstrip()).lstrip()
                store_info['name'] = line
            elif u'位：' in line or u'位:' in line:
                line = self.remove_colon(line.lstrip()).lstrip()
                store_info['price_range'] = line
            if (store_info['address'] and store_info['phone'] and store_info['name']
                and store_info['price_range']):
                break
        return store_info

    def get_store_info(self, data):
        store_info = {'name': None, 'url': None, 'phone': None, 'address': None,
                      'price_range': None}
        raw_text = data.text.split('\n')
        text = [raw_text_elem for raw_text_elem in raw_text if raw_text_elem != '']
        try:
            metadata = data.findAll(attrs={'name': 'description'})[0]['content'].split('\n')
            metadata = [meta for meta in metadata if meta != '']
            store_info = self.extract_store_info(metadata, store_info)
        except:
            pass
        store_info.update(self.extract_store_info(text, store_info))
        return store_info

def main(url):
    crawler = ptt_crawler()
    root_page = crawler.get_page(url)
    root_page_data = BeautifulSoup(root_page)
    count = 0
    store_info = None
    end_reached = False
    while True:
        title_lst = crawler.get_title_list(root_page_data)
        for title in title_lst:
            if u'食記' in title.text and not title.text.startswith('Re:'):
                store_info = None
                # List of 'blackholes'
                if title.a['href'] in ['/bbs/Food/M.1376585048.A.EAA.html',
                                       '/bbs/Food/M.1345599928.A.C5E.html',
                                       '/bbs/Food/M.1335827893.A.E6C.html',
                                       '/bbs/Food/M.1334503278.A.239.html']:
                    continue
                if title.a['href'] == '/bbs/Food/M.1327665674.A.407.html':
                    print "Reached 2012/1/1"
                    end_reached = True
                    break
                sub_page_data = BeautifulSoup(crawler.get_page("https://www.ptt.cc/{0}"
                                                       .format(title.a['href'])))
                store_info = crawler.get_store_info(sub_page_data)
                if store_info:
                    store_info['url'] = "https://www.ptt.cc{0}".format(title.a['href'])
                    if not store_info['name']:
                        store_info['name'] = title.text.split(']')[-1]
                    for key in store_info:
                        print key, store_info[key]
                    count += 1
                    print
        if end_reached:
            break
        next_mark = root_page_data.findAll('a', {'class': 'btn wide'})[1]
        if not next_mark:
            break
        else:
            root_page_data = BeautifulSoup(crawler.get_page("https://www.ptt.cc/{0}"
                                                    .format(next_mark['href'])))
    print "Total {0} blogs extracted".format(count)

if __name__ == "__main__":
    url = 'https://www.ptt.cc/bbs/Food/index.html'
    main(url)
