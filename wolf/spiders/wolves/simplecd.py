#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urllib
import urlparse
from scrapy import log
from scrapy.http import Request
from base.base_wolf import Base_Wolf
from pcnile.helper import group_list

class Wolf(Base_Wolf):	
	def __init__(self, *args, **kwargs):
		super(Wolf, self).__init__(*args, **kwargs)
		
		self.name = 'simplecd'
		self.seed_urls = [
			'http://simplecd.me/movie/',
		]
		self.base_url = 'http://simplecd.me/'
		self.anchor['follow'] = "//*[@class='entry-info']/a/@href"
		self.anchor['desc'] = "//*[@class='description']"

	def get_title(self, item, response, tree):
		try:
			item['title'] = tree.xpath("//*[@class='abstract']/h2")[0].text
			return item
		except IndexError:
			return super(Wolf, self).get_title(item, response, tree)
	
	def get_resource(self, item, response, tree):
		def build_url(url, qs):
			url_parts = list(urlparse.urlparse(url))
			url_parts[4] = urllib.urlencode(qs)
			return urlparse.urlunparse(url_parts)
		
		item = super(Wolf, self).get_resource(item, response, tree)
		group_keys = group_list(list(set(tree.xpath("//*[@type='checkbox']/@value"))), 50)
		if len(group_keys):
			group_qs = list()
			for keys in group_keys:
				qs = [('mode', 'seperate')]
				qs += [('rid', k) for k in keys]
				group_qs.append(qs)
			
			requests = [Request(build_url("http://simplecd.me/download/", qs), cookies=self.cookiejar._cookies) for qs in group_qs]
			return self.defer_download_list(item, requests, self.process_ed2k_finish, self.defer_download_fail_ignore, self.process_ed2k_done)
		else:
			self.log("DropItem %s" % item['source'], level=log.WARNING)
			return None
	
	def process_ed2k_finish(self, response, request):
		ed2k = list()
		
		tree = self.etree_fromresponse(response)
		for r in [r for r in list(set([r for r in tree.xpath("//a/@href")])) if r.startswith('ed2k')]:
			try:
				ed2k.append({'urn':r.split('|')[4].lower(), 'ed2k':r})
			except Exception as e:
				print e
		
		return ed2k
	
	def process_ed2k_done(self, results, item):
		for ok, value in results:
			if isinstance(value, list):
				item['resource']['ed2k'] += value
			else:
				self.log("process_ed2k_done %s" % item['source'], level=log.DEBUG)
		
		if self.has_resource(item):
			return item
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
