# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from .items import InstaPost, InstaFollower, InstaFollow, InstaUser
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import os

class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient(os.getenv('DATA_BASE'))['parse_inst_11_2']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection_name = spider.name
            if type(item) == InstaUser:
                collection_name += '_'+'User'
                collection = self.db[collection_name]
                collection.update_one({'_id':item['_id']}, {'$set':item}, upsert=True)
                return item    
            elif type(item) == InstaFollower:
                collection_name += '_'+'InstaFollower'
            else:
                collection_name += '_'+'InstaFollow'
            collection = self.db[collection_name]
            collection.insert_one(item)
        return item


class GbImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if type(item) == InstaPost:
            img_url = item.get('data')['thumbnail_resources'][-1]['src']
            if img_url:
                yield Request(img_url)

    def item_completed(self, results, item, info):
        if type(item) == InstaPost:
            item['img'] = results[0][1]['path']
        return item
