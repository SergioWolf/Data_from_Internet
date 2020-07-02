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
        self.db = client.instagram

    def process_item(self, item, spider):
        for i in range(len(spider.parse_user)):
            collection = self.db[spider.parse_user[i]]
            collection.update_one({'user_id': item['user_id']}, {'$set': item}, upsert=True)
        return item

# class InstagramparsPhotosPipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#        if item['user_photo']:
#            for img in item['user_photo']:
#                try:
#                    yield scrapy.Request(img, meta=item)   #Скачиваем фото и передает item через meta
#                except Exception as e:
#                    print(e)
#
#     def file_path(self, request, response=None, info=None):
#         item = request.meta             #Получаем item из meta
#         return item['username']+'/'+ os.path.basename(urlparse(request.url).path)
#
#     def item_completed(self, results, item, info):
#         if results:
#            item['user_photo'] = [itm[1] for itm in results if itm[0]]
#         return item

class InstagramparsPipeline:
    def process_item(self, item, spider):
        return item
