#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import urllib2
import urlparse
import warnings
import mechanize
import cookielib
import libtorrent
from time import time
from django.utils.encoding import force_unicode

warnings.filterwarnings("ignore", category=UserWarning)

class MultiCookieBrowser(object):
    def __init__(self, num):
        self.maxnum = num
        self.index = 0
        self.browser = [self._browser() for i in range(num)]
    
    def _browser(self):
        br = mechanize.Browser()
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)
        br.addheaders = [
            ('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.11) Gecko/20100701 Firefox/3.5.11')
        ]
        
        return br
    
    def get_browser(self):
        self.index = (self.index + 1) % self.maxnum
        return self.browser[self.index]

mcb = MultiCookieBrowser(30)

def check_torrent(content):
	try:
		metadata = libtorrent.bdecode(content)
		info = libtorrent.torrent_info(metadata)
		urn = str(info.info_hash()).lower()
		return urn
	except:
		return None

# 检测百度云链接是否存在
def check_baiduyun(url, br=None):
    if br == None:
        br = mcb.get_browser()
    try:
        res = br.open(url, timeout=15)
        if res.geturl() != 'http://pan.baidu.com/error/404.html':
            page = force_unicode(res.read())
            if len(re.findall(ur"(链接不存在|你所访问的页面不存在了)", page)) == 0:
                return True
    except:
        return True
    
    return False

def check_baiduyun_with_code(url, code):
    br = mcb.get_browser()
    
    try:
        res = br.open(url, timeout=15)
        res_url = res.geturl()
        if res_url != 'http://pan.baidu.com/error/404.html':
            if 'init' not in urlparse.urlparse(res_url).path:
                page = force_unicode(res.read())
                if len(re.findall(ur"(链接不存在|你所访问的页面不存在了)", page)) == 0:
                    return True
            else:
                data = "pwd={0}&vcode=".format(code)
                check_url = "{0}&t={1}&".format(res_url.replace('init', 'verify'), int(time()))
                mesg = br.open(check_url, data, timeout=15).read()
                errno = json.loads(mesg).get('errno')
                if errno == -63 or errno == -9:
                    return True
                return check_baiduyun(url, br)
    except:
        return True
    
    return False

if __name__ == '__main__':
    print check_baiduyun('http://pan.baidu.com/share/link?shareid=2447393167&uk=2653948094')
    print check_baiduyun_with_code('http://pan.baidu.com/s/1o6yTWvw', 'hv2z')