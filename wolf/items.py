#!/usr/bin/env python
# -*- coding: utf-8 -*-

from scrapy.item import Item, Field

class WolfItem(Item):
    source = Field() # source url
    title = Field()  # scrapy url title
    desc = Field()   # scrapy url desc
    identify = Field() # resource unique id
    resource = Field() # all resource structure
