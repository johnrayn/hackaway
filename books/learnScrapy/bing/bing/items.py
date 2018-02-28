# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field

class BingItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    Title = Field()
    Date = Field()

class CodewarsItem(scrapy.Item):
    image_urls = Field()
