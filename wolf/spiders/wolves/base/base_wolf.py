#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import urllib
import urllib2
import warnings
import urlparse
import cookielib
import mechanize
from lxml import etree

from scrapy import log
from scrapy.http import Request
from scrapy.item import BaseItem

from wolf import settings as setting
from wolf.check import check_baiduyun, check_baiduyun_with_code, check_torrent

from twisted.python.failure import Failure
from twisted.internet import reactor, defer, threads
from twisted.internet.defer import Deferred, DeferredList

warnings.filterwarnings("ignore", category=UserWarning)

class Base_Wolf(object):
	def __init__(self, spider):
		self.name = 'base_wolf'
		self.rule = {'title':'', 'desc':'', 'resource':[], 'follow':[], 'crawl':[]}
		self.anchor = {'title':'', 'desc':'', 'resource':[], 'follow':[], 'crawl':[]}
		self.seed_urls = []
		self.base_url = ""
		
		self.spider = spider
		self.log = spider.log
		self.uf = setting.UrlFilter
		self.cookiejar = cookielib.LWPCookieJar()
		
		br = mechanize.Browser()
		br.set_cookiejar(self.cookiejar)
		br.set_handle_equiv(True)
		br.set_handle_gzip(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		br.addheaders = [
			('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.11) Gecko/20100701 Firefox/3.5.11')
		]
		
		self.opener = br
	
	def url_filter(self, start_urls):
		return filter(lambda url : url not in self.uf, start_urls)
	
	# use re rule match good urls
	def get_start_urls_by_rule(self):
		start_urls = list()
		for seed in self.seed_urls:
			try:
				tree = self.etree_fromurl(seed, timeout=45)
			except:
				print "site page false %s" % seed
				continue
			
			follow_urls = list()
			for href in tree.xpath("//a/@href"):
				path = urlparse.urlparse(href).path.lstrip('/') # get path
				if isinstance(self.rule['follow'], list):
					for follow in self.rule['follow']:
						if follow.match(path):
							follow_urls.append(urlparse.urljoin(seed, href))
							break
				else:
					if self.rule['follow'].match(path):
						follow_urls.append(urlparse.urljoin(seed, href))
				
			if len(follow_urls) == 0:
				print "site item false %s" % seed
			else:
				start_urls += follow_urls
		
		return self.url_filter(start_urls)
	
	def get_start_urls_by_xpath(self):
		start_urls = list()
		for seed in self.seed_urls:
			try:
				tree = self.etree_fromurl(seed, timeout=30)
			except:
				print "site page false %s" % seed
				continue
			
			if isinstance(self.anchor['follow'], list):	
				follow_urls = [urlparse.urljoin(seed, href) for href in [tree.xpath(follow) for follow in self.anchor['follow']]]
			else:
				follow_urls = [urlparse.urljoin(seed, href) for href in tree.xpath(self.anchor['follow'])]
			
			if len(follow_urls) == 0:
				print "site item false %s" % seed
			else:
				start_urls += follow_urls
		
		return self.url_filter(start_urls)
	
	def get_start_urls(self):
		if self.anchor['follow'] and self.rule['follow']:
			raise ValueError('%s: xpath and rule, only one can exist' % self.name)
		elif self.anchor['follow']:
			start_urls = self.get_start_urls_by_xpath()
		elif self.rule['follow']:
			start_urls = self.get_start_urls_by_rule()
		else:
			raise ValueError('xpath and rule, must exist one')
		
		return self.url_filter(start_urls)
	
	def make_requests_from_url(self, url):
		return Request(
			url = url,
			dont_filter=True,
			cookies=self.cookiejar._cookies,
			meta={'callback':self.process_request, 'tree':True}
		)
	
	"""
	中间处理函数不要处理任何异常，由最后使用节点处理异常
	"""
	def etree_fromurl(self, url, timeout=30):
		html = self.opener.open(url, timeout=timeout).read()
		return self.etree_fromstring(html)
	
	def etree_fromresponse(self, response):
		return self.etree_fromstring(response.body)
	
	def etree_fromstring(self, html):
		tree = etree.fromstring(html, etree.HTMLParser(remove_comments=True))
		etree.strip_elements(tree, 'script')
		return tree
	
	"""
	Item通用处理函数
	"""
	def get_title(self, item, response, tree):
		try:
			item['title'] = tree.xpath("//title")[0].text
		except IndexError:
			item['title'] = response.url
		
		return item
	
	def get_desc(self, item, response, tree):
		try:
			if self.anchor['desc']:
				try:
					info = tree.xpath(self.anchor['desc'])[0]
				except IndexError:
					info = tree
			else:
				info = tree
			
			desc = os.linesep.join(filter(lambda l: l != '', [l.strip() for l in info.xpath(".//text()")]))
			item['desc'] = desc
		except Exception as e:
			self.log("get_desc %s" % item['source'], level=log.WARNING)
			item['desc'] = ''
		
		return item
	
	def get_unique_identify(self, item, response, tree):
		item['identify'] = {'douban':'', 'imdb':''}
		return item
	
	def get_resource(self, item, response, tree):
		item['resource'] = {'bt':[], 'ed2k':[], 'netdisk':[], 'online':[], 'http':[]}
		return item
	
	def has_resource(self, item):
		for k,v in item['resource'].items():
			if len(v):
				return True
		else:
			return False
	
	def filter_page(self, response, tree):
		return False
	
	def process_request(self, item, response, tree):
		if response.meta['tree'] == True:
			tree = self.etree_fromresponse(response)
		
		# filter page by site some keywords
		if not self.filter_page(response, tree):
			item['source'] = response.url
			
			dfd = defer.maybeDeferred(self.get_title, item, response, tree)
			dfd.addCallback(self.get_desc, response, tree)
			dfd.addCallback(self.get_unique_identify, response, tree)
			dfd.addCallback(self.get_resource, response, tree)
			
			return dfd
		else:
			return None
	
	"""
	异步到同步的下载处理器
	"""
	def defer_download_list(self, item, requests, callback, errback, doneback):
		dlist = [self.defer_download(r, callback, errback) for r in requests]
		dfd = DeferredList(dlist, consumeErrors=1)
		dfd.addBoth(doneback, item)
		
		return dfd
	
	def defer_download(self, request, callback, errback):
		request.meta['handle_httpstatus_all'] = True
		dfd = self.spider.crawler.engine.download(request, self.spider)
		dfd.addErrback(errback, request)
		dfd.addCallback(callback, request)
		return dfd
	
	def defer_download_fail_ignore(self, failure, request):
		return None
	
	"""
	处理BT种子下载
	"""
	def process_bt_finish(self, response, request):
		urn = check_torrent(response.body)
		if urn:
			return {'urn':urn, 'torrent':response.body}
		else:
			return None
	
	def process_bt_done(self, results, item):
		for ok, value in results:
			if isinstance(value, dict):
				item['resource']['bt'].append(value)
			else:
				self.log("download_bt %s" % item['source'], level=log.DEBUG)
		
		if self.has_resource(item):
			return item
		else:
			self.log("DropItem %s" % item['source'], level=log.WARNING)
			return None
	
	def download_bt(self, item, requests):
		return self.defer_download_list(item, requests, self.process_bt_finish, self.defer_download_fail_ignore, self.process_bt_done)
	
	"""
	百度云链接检测线程
	"""
	# in defer thread
	def netdisk_check_finish(self, resource):
		goods = list()
		for r in resource:
			if r['code'] == '':
				if check_baiduyun(r['link']):
					goods.append(r)
			else:
				if check_baiduyun_with_code(r['link'], r['code']):
					goods.append(r)
		
		return goods
	
	# defer threading callback
	def netdisk_check_done(self, result, item):
		if len(result):
			item['resource']['netdisk'] = result
			return item
		else:
			self.log("DropItem %s" % item['source'], level=log.WARNING)
			return None
	
	def netdisk_check(self, item, resource):
		dfd = threads.deferToThread(self.netdisk_check_finish, resource)
		dfd.addCallback(self.netdisk_check_done, item)
		return dfd
