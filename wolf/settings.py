# -*- coding: utf-8 -*-

import os.path
import pymongo
import platform
from pcnile import sqlitedict as bsddb

BOT_NAME = 'wolf'

SPIDER_MODULES = ['wolf.spiders']
NEWSPIDER_MODULE = 'wolf.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36'

LOG_LEVEL = 'INFO'

CONCURRENT_REQUESTS = 10
COOKIES_ENABLED = True
DOWNLOAD_DELAY = 0
DOWNLOAD_TIMEOUT = 45
REDIRECT_MAX_TIMES = 3

EXTENSIONS = {
    'scrapy.webservice.WebService': None,
    'scrapy.telnet.TelnetConsole': None,
    'scrapy.contrib.memusage.MemoryUsage': None,
    'scrapy.contrib.memdebug.MemoryDebugger': None,
    'scrapy.contrib.spiderstate.SpiderState': None,
    'scrapy.contrib.throttle.AutoThrottle': None,
    'scrapy.contrib.feedexport.FeedExporter': None,
    'wolf.feedexport.FeedExporter' : 500,
}

LOG_FILE = 'log.log'

# set all kinds of filter
if platform.system() == 'Linux':
    DBDIR = '/opt/db/wolf'
else:
    DBDIR = 'D:\\obtainfo\\Store\\db'
UrlFilter = bsddb.open(os.path.join(DBDIR, 'url.db'), autocommit=True)
BtFilter = bsddb.open(os.path.join(DBDIR, 'bt.db'), autocommit=True)
Ed2kFilter = bsddb.open(os.path.join(DBDIR, 'ed2k.db'), autocommit=True)
NetdiskFilter = bsddb.open(os.path.join(DBDIR, 'netdisk.db'), autocommit=True)
OnlineFilter = bsddb.open(os.path.join(DBDIR, 'online.db'), autocommit=True)

if platform.system() == 'Linux':
    TORRENT_DIR = '/opt/db/torrent'
else:
    TORRENT_DIR = 'D:\\obtainfo\\Store\\torrent'

# mongodb store
Collection = pymongo.Connection().scrapy.wolf
