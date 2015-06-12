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
		
		self.name = 'btpanda'
		self.seed_urls = [
			'http://www.btpanda.com/thread-htm-fid-5.html',
			'http://www.btpanda.com/thread-htm-fid-20.html',
		]
		self.base_url = 'http://www.btpanda.com/'
		self.rule['follow'] = re.compile(r'read-htm-tid-\d+.html')
		self.anchor['desc'] = "//*[@id='read_tpc']"
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		resource = tree.xpath("//a/@href")
		downloads = [urlparse.urljoin(self.base_url, r) for r in resource if re.match(r'job.php\?action=download&aid=', r)]
		
		if len(downloads):
			return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
