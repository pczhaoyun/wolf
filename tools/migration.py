#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import codecs
import os.path
import pymongo
import platform
import urlparse
from pcnile import sqlitedict as bsddb

DBDIR = '.'

def magnet():
    record_bt = dict()
    BtFilter = bsddb.open(os.path.join(DBDIR, 'bt.db'), autocommit=False)
    
    with codecs.open('urn.json', 'rb', 'utf-8') as f:
        for j in json.load(f):
            record_bt[j] = int(time.time()*1000)
    
    BtFilter.update(record_bt)
    BtFilter.commit()
    BtFilter.close()

def ed2k_and_netdisk():
    Ed2kFilter = bsddb.open(os.path.join(DBDIR, 'ed2k.db'))
    NetdiskFilter = bsddb.open(os.path.join(DBDIR, 'netdisk.db'))
    
    record_netdisk, record_ed2k = dict(), dict()
    db = pymongo.Connection().server
    for r in db.resource.find():
        for n in r['netdisk']:
            record_netdisk[n['link']] = int(time.time()*1000)
        
        if 'complete' not in r:
            r['complete'] = r['stereo'] + r['hd'] + r['dvd'] + r['cam']
        
        for c in r['complete']:
            if c['link'].startswith('ed2k'):
                record_ed2k[c['link'].split('|')[4].lower()] = int(time.time()*1000)
    
    NetdiskFilter.update(record_netdisk)
    NetdiskFilter.commit()
    NetdiskFilter.close()
    
    Ed2kFilter.update(record_ed2k)
    Ed2kFilter.commit()
    Ed2kFilter.close()

def url():
    UrlFilter = bsddb.open(os.path.join(DBDIR, 'url.db'))
    record_url = dict()
    
    con = pymongo.Connection()
    for i in con.server.info.find({'type':'movie'}):
        for u in i['samesite']:
            record_url[u] = int(time.time()*1000)
    
    for i in list(con.scrapy.fast.find()) + list(con.scrapy.filter.find()) + list(con.netdisk.scrapy.find()) + list(con.netdisk.filter.find()):
        if isinstance(i['source'], list):
            for u in i['source']:
                record_url[u] = int(time.time()*1000)
        else:
            record_url[i['source']] = int(time.time()*1000)
    
    good_url = dict()
    for k, v in record_url.items():
        url_parts = list(urlparse.urlparse(k))
        netloc = url_parts[1]
        
        if netloc == 'imax.im':
            continue
        elif netloc == 'www.tbmovie.com':
            url_parts[1] = 'www.lanyingwang.com'
            good_url[urlparse.urlunparse(url_parts)] = int(time.time()*1000)
        else:
            good_url[k] = v
    
    UrlFilter.update(good_url)
    UrlFilter.commit()
    UrlFilter.close()

if __name__ == '__main__':
    url()
    magnet()
    ed2k_and_netdisk()
