#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import random
import urlparse
from scrapy import log
from scrapy.http import FormRequest
from base.base_wolf import Base_Wolf

class Wolf(Base_Wolf):
	def __init__(self, *args, **kwargs):
		super(Wolf, self).__init__(*args, **kwargs)
		
		self.name = 'bttiantang'
		self.seed_urls = [
			'http://www.bttiantang.com/',
		]
		self.base_url = 'http://www.bttiantang.com/'
		self.anchor['follow'] = "//*[@class='tt cl']/a/@href"
		self.anchor['desc'] = "//*[@class='moviedteail_list']"
	
	def get_title(self, item, response, tree):
		try:
			item['title'] = tree.xpath("//*[@class='moviedteail_tt']/h1")[0].text
			return item
		except IndexError:
			return super(Wolf, self).get_title(item, response, tree)
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		tinfo = tree.xpath("//*[@class='tinfo']/a/@href")
		downloads = list()
		for url in tinfo:
			qs = urlparse.parse_qs(urlparse.urlparse(url).query)
			data = {'action':'download', 'down':'d1'}
			data['id'] = qs['id'][0]
			data['uhash'] = qs['uhash'][0]
			data['imageField.x'] = str(random.randint(10, 129))
			data['imageField.y'] = str(random.randint(10, 39))
			downloads.append(data)
		
		if len(downloads):
			requests = [FormRequest("http://www.bttiantang.com/download.php", formdata=d) for d in downloads]
			return self.download_bt(item, requests)
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
