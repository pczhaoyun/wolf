#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urlparse
import HTMLParser

from lxml import etree
from django.utils.encoding import force_unicode

from scrapy import log
from scrapy.http import Request
from base.base_wolf import Base_Wolf

re_name = re.compile(ur"(迅雷下载|\(微电影\)|\[高清\]|\[高清\]|\[国配\]|\[3D\]|\[720P\]|\(2013\))")
re_code = re.compile(ur"密码：(\w+)")
re_split = re.compile(ur'[^,: ]+', re.U)

class Wolf(Base_Wolf):
    def __init__(self, *args, **kwargs):
        super(Wolf, self).__init__(*args, **kwargs)

        self.name = '3mu'
        self.seed_urls = [
            'http://www.3mu.cc/',
        ]
        self.base_url = 'http://www.3mu.cc/'
        self.anchor['follow'] = "//*[@class='wptip']/../a/@href"
        self.anchor['desc'] = "//*[@class='webzi_top']"

    def get_title(self, item, response, tree):
        try:
            title = force_unicode(tree.xpath("//*[@class='webzi_top']/ul/li/h1")[0].text.replace(u'迅雷下载', '').strip())
            item['title'] = re_name.sub('', title).strip()
        except IndexError:
            item = super(Wolf, self).get_title(item, response, tree)

        return item

    def get_resource(self, item, response, tree):
        item = super(Wolf, self).get_resource(item, response, tree)

        # extract
        urls = set()
        for a in tree.xpath("//a"):
            try:
                href = a.xpath("@href")[0]
                if href.startswith('/pan/'):
                    urls.add(urlparse.urljoin(self.base_url, href))
            except IndexError:
                pass

        downloads = urls
        if len(downloads):
            requests = [Request(d, dont_filter=True, cookies=self.cookiejar._cookies,) for d in downloads]
            return self.defer_download_list(item, requests, self.process_netdisk_finish, self.defer_download_fail_ignore, self.process_netdisk_done)
        else:
            self.log("DropItem %s" % item['source'], level=log.WARNING)
            return None

    def process_netdisk_finish(self, response, request):
        resource = list()

        tree = self.etree_fromresponse(response)
        for i in tree.xpath("//*[@class='panbox-l-c']/li/a"):
            try:
                if len(re.findall(ur"(预告片|花絮|先行版)", i.text)) == 0:
                    resource.append({'link':i.xpath('@href')[0], 'info':i.text})
            except IndexError:
                pass

        for r in resource:
            try:
                code = re_code.findall(r['info'])[0]
                r['code'] = code
            except IndexError:
                r['code'] = ''

        return resource

    def process_netdisk_done(self, results, item):
        for ok, value in results:
            if isinstance(value, list):
                item['resource']['netdisk'] += value
            else:
                self.log("process_netdisk_done %s" % item['source'], level=log.DEBUG)

        if self.has_resource(item):
            return self.netdisk_check(item, item['resource']['netdisk'])
        else:
            self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
            return None
