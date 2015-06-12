#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urlparse
from scrapy import log
from scrapy.http import Request
from base.base_wolf import Base_Wolf

class Wolf(Base_Wolf):	
    def __init__(self, *args, **kwargs):
        super(Wolf, self).__init__(*args, **kwargs)

        self.name = 'btbbt'
        self.seed_urls = [
            'http://www.btbbt.cc/forum-index-fid-951.htm',
            'http://www.btbbt.cc/forum-index-fid-1183.htm',
        ]
        self.base_url = 'http://www.btbbt.cc/'
        self.rule['follow'] = re.compile(r'thread-index-fid-\d+-tid-\d+.htm')
        self.anchor['desc'] = "//*[@class='bg1 border post']"

    def get_resource(self, item, response, tree):
        item = super(Wolf, self).get_resource(item, response, tree)

        resource = tree.xpath("//*[@class='attachlist']//a/@href")
        downloads = [r.replace('dialog', 'download') for r in resource if 'attach-dialog' in r]

        if len(downloads):
            return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
        else:
            self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
            return None
