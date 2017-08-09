# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BBallItem(scrapy.Item):
    id = scrapy.Field()
    teams = scrapy.Field()
    time = scrapy.Field()
    event = scrapy.Field()
    score = scrapy.Field()

