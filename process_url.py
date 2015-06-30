#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import locale
import codecs
import urllib
import json
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen, build_opener
from page_crawler import ptt_crawler

# ref: http://xiaosu.blog.51cto.com/2914416/1340932
reload(sys)
sys.setdefaultencoding('utf8')

# ref: http://stackoverflow.com/questions/4545661/unicodedecodeerror
#      -when-redirecting-to-file
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

crawler = ptt_crawler()
buf = ''
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line == '':
            if 'img' in buf:
                print buf
            buf = ''
        else:
            buf = '{0}\n{1}'.format(buf, line)
        # extract image urls
        if line.startswith('blog_url'):
            try:
                soup = BeautifulSoup(crawler.get_page(line.split(' ')[1]))
                buf = '{0}\nblogtitle {1}'.format(buf, soup.find('title').text)
                for item in soup.findAll('img'):
                    if 'jpg' in item['src'] and ('pimg' in item['src']
                                                 or 'staticflickr' in item['src']):
                        buf = '{0}\nimg {1}'.format(buf, item['src'])
            except:
                pass
        # get position
        if line.startswith('address'):
            try:
                x, y = crawler.get_pos(line.split(' ')[1])
                buf = '{0}\nposition {1},{2}'.format(buf, x, y)
            except:
                pass
