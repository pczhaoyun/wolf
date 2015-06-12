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
		
		self.name = 'yayaxz'
		self.seed_urls = [
			'http://www.yayaxz.com/resources?c=only_movie&render-format=table&s=updated_at&page=1',
		]
		self.base_url = 'http://www.yayaxz.com/'
		self.anchor['follow'] = "//*[@class='resource-dq-item']/a/@href"
		self.anchor['desc'] = "//*[@class='resource-detail-txt fl']"
	
	# not filter
	def get_start_urls(self):
		return self.get_start_urls_by_xpath()
	
	def get_title(self, item, response, tree):
		try:
			title = tree.xpath("//*[@id='favi-links-container']/a")[0].text
			item['title'] = re.match(ur"《(.+)》", title).group(1)
			return item
		except IndexError:
			return super(Wolf, self).get_title(item, response, tree)
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		ed2k = list()
		for r in [r for r in list(set([r for r in tree.xpath("//a/@href")])) if r.startswith('ed2k')]:
			try:
				ed2k.append({'urn':r.split('|')[4].lower(), 'ed2k':r})
			except Exception as e:
				print e
		item['resource']['ed2k'] = ed2k
		
		if len(ed2k):
			return item
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
