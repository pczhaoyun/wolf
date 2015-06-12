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
		
		self.name = 'cnscg'
		self.seed_urls = [
			'http://www.cnscg.org/',
		]
		self.base_url = 'http://www.cnscg.org/'	
		self.rule['follow'] = re.compile(r'show-')
		self.anchor['desc'] = "//*[@class='intro']"
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		resource = tree.xpath("//*[@class='original download']//a/@href")
		downloads = [urlparse.urljoin(self.base_url, r) for r in resource if re.match(r'down.php', r)]
		
		if len(downloads):
			return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
