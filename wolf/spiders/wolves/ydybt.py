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
		
		self.name = 'ydybt'
		self.seed_urls = [
			'http://www.ydybt.com/',
		]
		self.base_url = 'http://www.ydybt.com/'
		self.anchor['follow'] = "//*[@class='thumbnail']/a/@href"
		self.anchor['desc'] = "//*[@id='post_content']"
	
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
