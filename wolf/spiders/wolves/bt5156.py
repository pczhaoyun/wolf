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
		
		self.name = 'bt5156'
		self.seed_urls = [
			'http://bbs.bt5156.net/thread.php?fid-9.html',
			'http://bbs.bt5156.net/thread.php?fid-8.html',
		]
		self.base_url = 'http://bbs.bt5156.net/'
		self.rule['follow'] = re.compile(r'read.php')
		self.anchor['desc'] = "//*[@id='read_tpc']"
	
	def get_title(self, item, response, tree):
		item = super(Wolf, self).get_title(item, response, tree)
		
		try:
			item['title'] = re.findall("\[(.+?)\]", item['title'])[2]
		except IndexError:
			pass
		
		return item
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		resource = tree.xpath("//*[@class='tr1 r_one']//a/@href")
		downloads = [urlparse.urljoin(url, r) for r in resource if re.match(r'job.php', r)]
		
		resource = re.findall(r"http://bbs.bt5156.net/job.php\?action=download&pid=(\w+)&tid=(\d+)&aid=(\d+)", response.body)
		downloads += ["http://bbs.bt5156.net/job.php?action=download&pid=%s&tid=%s&aid=%s" % r for r in resource]
		
		if len(downloads):
			return self.download_bt(item, [Request(d, cookies=self.cookiejar._cookies,) for d in downloads])
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
