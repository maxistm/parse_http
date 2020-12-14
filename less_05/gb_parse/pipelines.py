# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from .items import HhunterVacancyItem, HhunterCompanyItem


class GbParsePipeline:
    def __init__(self):
        self.db = MongoClient()['parse_hh_11_2']
    
    def process_item(self, item, spider):
        if spider.db_type == 'MONGO':
            collection_name = spider.name
            if type(item) == HhunterCompanyItem:
                collection_name += '_company'
            else:
                collection_name += '_vacancy'
            collection = self.db[collection_name]
            #collection.insert_one(item)
        return item
