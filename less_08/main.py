from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from gb_parse.spiders.instagramchain import InstagramChainSpider
import dotenv
import os
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue



def get_next_freinds(query):

    next_level = {}
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramChainSpider, login=os.getenv('LOGIN'),
                    enc_password=os.getenv('PASSWORD'), next_level = next_level, query = query )
    crawl_proc.start()
    crawl_proc = None
    


dotenv.load_dotenv()
visited_users = []
if __name__ == '__main__':
    query = ['trillij', 'pshigoda']
    configure_logging()
    get_next_freinds(query)
    #result, quere = bfs('maxisfx', 'trillij')
    print(query)
