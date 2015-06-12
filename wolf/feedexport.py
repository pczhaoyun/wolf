#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time

from scrapy import log, signals
from wolf import settings as setting
from pcnile.resource import format_bt_by_content, format_ed2k

TORRENT_DIR = setting.TORRENT_DIR

def save_torrent(urn, torrent):
	try:
		if not os.path.exists(TORRENT_DIR):
			os.mkdir(TORRENT_DIR)
		
		with open(os.path.join(TORRENT_DIR, "%s.torrent" % urn), 'wb') as f:
			f.write(torrent)
		
		return format_bt_by_content(torrent)
	except Exception as e:
		print e
	
	return None

def save_ed2k(urn, ed2k):
	try:
		return format_ed2k(ed2k)
	except Exception as e :
		print e
	
	return None

class FeedExporter(object):
	def __init__(self, settings):
		self.itemcount = 0
		self.settings = settings
		self.bf = setting.BtFilter
		self.uf = setting.UrlFilter
		self.ef = setting.Ed2kFilter
		self.of = setting.OnlineFilter
		self.nf = setting.NetdiskFilter
		self.collection = setting.Collection
	
	@classmethod
	def from_crawler(cls, crawler):
		o = cls(crawler.settings)
		crawler.signals.connect(o.item_scraped, signals.item_scraped)
		crawler.signals.connect(o.close_spider, signals.spider_closed)
		return o
	
	def close_spider(self, spider):
		self.bf.close()
		self.uf.close()
		self.ef.close()
		self.of.close()
		self.nf.close()
	
	def item_scraped(self, item, spider):
		hitem, item = item, dict(item)
		
		resource = item['resource']
		
		# 1. make all kinds of resource unique
		resource['bt'] = filter(lambda b : b['urn'] not in self.bf, resource['bt'])
		resource['ed2k'] = filter(lambda b : b['urn'] not in self.ef, list(resource['ed2k']))
		resource['netdisk'] = filter(lambda b : b['link'] not in self.nf, resource['netdisk'])
		resource['online'] = filter(lambda b : b['link'] not in self.of, resource['online'])
		
		# 2. record all resource
		record_bt = dict()
		for b in resource['bt']:
			record_bt[b['urn']] = int(time.time()*1000)
		
		record_ed2k = dict()
		for b in resource['ed2k']:
			record_ed2k[b['urn']] = int(time.time()*1000)
		
		record_netdisk = dict()
		for b in resource['netdisk']:
			record_netdisk[b['link']] = int(time.time()*1000)
		
		# 3. format all resource
		resource['bt'] = filter(lambda b : b is not None, [save_torrent(b['urn'], b['torrent']) for b in resource['bt']])
		resource['ed2k'] = filter(lambda b : b is not None, [save_ed2k(b['urn'], b['ed2k']) for b in resource['ed2k']])
		
		# 4. if still has resource, we save it
		if len(resource['bt']) or len(resource['ed2k']) or len(resource['netdisk']) or len(resource['online']):
			self.itemcount += 1
			
			resource['complete'] = resource['bt'] + resource['ed2k']
			del resource['bt'], resource['ed2k']
			resource['episode'] = []
			
			if self.collection.find({'source':item['source']}).count() == 0: #add new
				item['source'] = [item['source']]
				self.collection.insert(item)
			else:
				i = self.collection.find_one({'source':item['source']})
				i['resource']['complete'] += item['resource']['complete']
				i['resource']['netdisk'] += item['resource']['netdisk']
				i['resource']['online'] += item['resource']['online']
				self.collection.save(i)
			
			# push all resource to dupefilter
			self.bf.update(record_bt)
			self.ef.update(record_ed2k)
			self.nf.update(record_netdisk)
		
		# 5. always add target url to url filter db
		if isinstance(item['source'], list):
			for source in item['source']:
				self.uf[source] = int(time.time()*1000)
		else:
			self.uf[item['source']] = int(time.time()*1000)
		
		return hitem
