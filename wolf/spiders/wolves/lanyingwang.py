#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os.path
import urlparse
from scrapy import log
from scrapy.http import Request
from base.base_wolf import Base_Wolf

class Wolf(Base_Wolf):	
    def __init__(self, *args, **kwargs):
        super(Wolf, self).__init__(*args, **kwargs)

        self.name = 'lanyingwang'
        self.seed_urls = [
            'http://www.lanyingwang.com/category/share',
            'http://www.lanyingwang.com/category/share/page/2',
        ]
        self.base_url = 'http://www.lanyingwang.com/'
        self.anchor['follow'] = "//*[@class='archive_title']/h3/a/@href"
        self.anchor['desc'] = "//*[@id='entry']"

    def get_resource(self, item, response, tree):
        def urljoin(base, url):
            join = urlparse.urljoin(base, url)
            path = os.path.normpath(urlparse.urlsplit(join).path).replace('\\', '/')
            url = urlparse.urljoin(base, path)
            return url

        item = super(Wolf, self).get_resource(item, response, tree)

        resource = tree.xpath("//a/@href")
        downloads = [urljoin(self.base_url, r) for r in resource if r.endswith('.torrent')]

        if len(downloads):
            return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
        else:
            self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
            return None
