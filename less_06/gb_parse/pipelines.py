# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from .items import HhunterVacancyItem, HhunterCompanyItem, InstaPost
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_hh_11_2']

    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection_name = spider.name
            """
            для hh
            if type(item) == HhunterCompanyItem:
                collection_name += '_company'
            else:
                collection_name += '_vacancy'
            """
            collection = self.db[collection_name]
            # collection.insert_one(item)
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
