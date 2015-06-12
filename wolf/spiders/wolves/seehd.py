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
		
		self.name = 'seehd'
		self.seed_urls = [
			'http://bbs.seehd.co/forum.php?gid=1',
		]
		self.base_url = 'http://bbs.seehd.co/'
		self.rule['follow'] = re.compile(r'thread-\d+-1-1')
		self.anchor['desc'] = "//*[@id='JIATHIS_CODE_HTML4']"
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		if re.findall(ur"下载积分", response.body):
			return None
		
		resource = tree.xpath("//a/@href")
		downloads = [urlparse.urljoin(self.base_url, r) for r in resource if re.match(r'forum.php\?mod=attachment', r)]
		
		if len(downloads):
			return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
