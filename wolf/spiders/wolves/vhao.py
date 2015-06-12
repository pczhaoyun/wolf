#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urlparse
import StringIO
import HTMLParser

from lxml import etree
from django.utils.encoding import force_unicode

from scrapy import log
from scrapy.http import Request
from base.base_wolf import Base_Wolf
from twisted.internet import threads, defer

re_name = re.compile(ur"\[.+\]")
re_code = re.compile(ur"码(\w{4})")
re_code2 = re.compile(ur"提取码(\w{4})")
re_split = re.compile(ur'[^,: ]+', re.U)
re_html_string = re.compile(r'</?\w+[^>]*>')
re_url = re.compile(ur'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
html_parser = HTMLParser.HTMLParser()

class Wolf(Base_Wolf):
    def __init__(self, *args, **kwargs):
        super(Wolf, self).__init__(*args, **kwargs)

        self.name = '6vhao'
        self.seed_urls = [
            'http://www.6vhao.net/',
        ]
        self.base_url = 'http://www.6vhao.net/'
        self.anchor['follow'] = "//*[@class='tjlist']/ul/li/a/@href"
        self.anchor['desc'] = "//*[@id='text']"

    def get_title(self, item, response, tree):
        try:
            title = force_unicode(tree.xpath("//*[@class='contentinfo']/h1")[0].text)
        except:
            title = url

        try:
            title = title.replace(u"】", '').replace(u"【", '')
            item['title'] = re_name.sub('', title).strip()
        except IndexError:
            item['title'] = title

        return item

    def get_resource(self, item, response, tree):
        item = super(Wolf, self).get_resource(item, response, tree)

        # extract
        resource = list()
        for l in StringIO.StringIO(etree.tostring(tree, encoding='unicode')):
            new_l = re_html_string.sub('', l)

            try:
                urls = [u for u in re_url.findall(new_l) if 'pan.baidu.com' in u][0]
            except:
                continue

            try:
                codes = re_code.findall("".join(re_split.findall(new_l)))[0]
            except:
                codes = ''

            resource.append({'link':urls, 'code':codes, 'info':new_l})

        if len(resource):
            return self.netdisk_check(item, resource)
        else:
            self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
            return None
