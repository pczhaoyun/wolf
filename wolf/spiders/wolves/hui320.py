#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urlparse
import StringIO
import HTMLParser

from lxml import etree
from django.utils.encoding import force_unicode

from scrapy import log
from scrapy.http import Request
from base.base_wolf import Base_Wolf
from twisted.internet import threads, defer

re_name = re.compile(ur"《(.+)》")
re_url = re.compile(ur'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
re_code = re.compile(ur"码(\w{4})")
re_code2 = re.compile(ur"提取码(\w{4})")
re_split = re.compile(ur'[^,：: ]+', re.U)
re_html_string = re.compile(r'</?\w+[^>]*>')
html_parser = HTMLParser.HTMLParser()

class Wolf(Base_Wolf):
	def __init__(self, *args, **kwargs):
		super(Wolf, self).__init__(*args, **kwargs)
		
		self.name = 'hui320'
		self.seed_urls = [
			'http://www.hui320.com/xin/hmovies',
			'http://www.hui320.com/xin/banime',
		]
		self.base_url = 'http://www.hui320.com/'
		self.anchor['follow'] = "//*[@class='excerpt']//h2/a/@href"
		self.anchor['desc'] = "//*[@class='article-content']"
	
	def get_resource(self, item, response, tree):
		item = super(Wolf, self).get_resource(item, response, tree)
		
		# extract
		resource = list()
		for l in StringIO.StringIO(etree.tostring(tree, encoding='unicode')):
			new_l = re_html_string.sub('', l)
			
			try:
				urls = [u for u in re_url.findall(l) if 'pan.baidu.com' in u][0]
			except:
				continue
			
			try:
				codes = re_code.findall("".join(re_split.findall(new_l)))[0]
			except:
				codes = ''
			
			resource.append({'link':urls, 'code':codes, 'info':new_l})
		
		if len(resource):
			return self.netdisk_check(item, resource)
		else:
			self.log("No Resource DropItem %s" % item['source'], level=log.WARNING)
			return None
