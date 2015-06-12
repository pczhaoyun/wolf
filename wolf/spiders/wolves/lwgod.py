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

        self.name = 'lwgod'
        self.seed_urls = [
            'http://www.lwgod.com/forum-18-1.html',
            'http://www.lwgod.com/forum-34-1.html',
            'http://www.lwgod.com/forum-36-1.html',
        ]
        self.base_url = 'http://www.lwgod.com/'
        self.rule['follow'] = re.compile(r'thread-\d+-1-1')
        self.anchor['desc'] = "//*[@class='t_msgfontfix']"

    def get_resource(self, item, response, tree):
        item = super(Wolf, self).get_resource(item, response, tree)

        resource = tree.xpath("//*[@class='t_msgfontfix']//a/@href")
        downloads = [urlparse.urljoin(self.base_url, r) + '&downconfirm=2' for r in resource if re.match(r'attachment.php', r)]

        if len(downloads):
            return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
        else:
            self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
            return None
