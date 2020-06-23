# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class BookparserPipeline:
    def __init__(self):                             #Конструктор, где инициализируем подключение к СУБД
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.book_scrapy

    def process_item(self, item, spider):
        if spider.name == 'book24ru':
            if item['price_basic'] == None or item['price_basic'] < item['price_discount']:
                item['price_basic'], item['price_discount'] = item['price_discount'], item['price_basic']
            collection = self.mongo_base[spider.name]
            collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
        elif spider.name == 'labirintru':
            if item['price_discount'] != None:
                item['price_discount'] = item['price_discount'][1]
            if item['author'] != []:
                item['name'] = item['name'].split(':')[1]
            collection = self.mongo_base[spider.name]
            collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)

        return item
