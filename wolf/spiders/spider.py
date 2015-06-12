#!/usr/bin/env python
# -*- coding: utf-8 -*-

# python lib
from multiprocessing.pool import ThreadPool

# core include lib
from scrapy import log
from scrapy.http import Request
from scrapy.spider import Spider

# project lib
from wolf.items import WolfItem
from wolf.spiders.wolves import get_wolves

# return tuple(wolves_index, urls)
def get_start_urls(wolves, pool_size=10):
    try:
        pool = ThreadPool(min(len(wolves), pool_size))
        start_urls = pool.map(lambda wolf : wolf.get_start_urls(), wolves)
        pool.close()
        pool.join()
    except Exception as e:
        print 'get_start_urls', e
        start_urls = map(lambda wolf : wolf.get_start_urls(), wolves) # for debug
    
    try:
        start_urls = [(k,v) for k,v in enumerate(start_urls)]
        start_urls = sorted(start_urls, key=lambda kv:len(kv[1]), reverse=True)
        level = len(start_urls[0][1])
        return (level, start_urls)
    except Exception as e:
        print 'get_start_urls', e
        return (0, [[] for i in range(len(wolves))])

class Wolves(Spider):
    name = 'wolf'
    
    def __init__(self, *args, **kwargs):
        super(Wolves, self).__init__(*args, **kwargs)
        
        self.wolves = get_wolves(self)
        self.level, self.global_start_urls = get_start_urls(self.wolves, pool_size=len(self.wolves)) # tuple(index, urls)
    
    # inverted sequence from big to small
    def start_requests(self):
        for level in range(self.level):
            for start_urls in self.global_start_urls:
                index, wolf_start_urls = start_urls # index for self.wolves
                try:
                    request = self.wolves[index].make_requests_from_url(wolf_start_urls[level])
                    request.callback = self.parse # patch callback function
                    yield request
                except IndexError:
                    break
    
    # router to wolf process handler
    def parse(self, response):
        try:
            try:
                item = response.meta['item']
            except KeyError:
                item = WolfItem()
            
            if response.meta['tree'] == True:
                dfd = response.meta['callback'](item, response, tree=None)
            else:
                dfd = response.meta['callback'](item, response, tree=None)
            
            return dfd
        except Exception as e:
            print 'spider parse error', e
            
        return None
