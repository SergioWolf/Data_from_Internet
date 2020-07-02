# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from scrapy.loader.processors import MapCompose, TakeFirst
import scrapy

def cleaner_price(price):
    if price:
        return int(price[0])
    else:
        return None

def cleaner_paramas(values):
    if values:
        return values.strip()
    else:
        return None

class DictCollector(object):

    def __call__(self, values):
        if values:
            return dict(zip(values[::2], values[1::2]))
        else:
            return None


class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    parameter = scrapy.Field(input_processor=MapCompose(cleaner_paramas), output_processor=DictCollector())
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(intput_processor=MapCompose(cleaner_price), output_processor=TakeFirst())
    currency = scrapy.Field(output_processor=TakeFirst())
    dimension = scrapy.Field(output_processor=TakeFirst())