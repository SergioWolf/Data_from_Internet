# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from urllib.parse import urlparse
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class DataBasePipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.leroymerlin

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.update_one({'link': item['link']}, {'$set': item}, upsert=True)
        return item

class LeroymerlinPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
       if item['photos']:
           for img in item['photos']:
               try:
                   yield scrapy.Request(img, meta=item)   #Скачиваем фото и передает item через meta
               except Exception as e:
                   print(e)

    def file_path(self, request, response=None, info=None):
        item = request.meta             #Получаем item из meta
        return item['name']+'/'+ os.path.basename(urlparse(request.url).path)

    def item_completed(self, results, item, info):
        if results:
           item['photos'] = [itm[1] for itm in results if itm[0]]
        return item