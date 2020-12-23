from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagramchain import InstagramChainSpider
import dotenv
import os

# from gb_parse import settings
dotenv.load_dotenv()
if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    next_level = {}
    crawl_proc.crawl(InstagramChainSpider, login=os.getenv('LOGIN'),
                     enc_password=os.getenv('PASSWORD'), next_level = next_level, users = ['maxisfx', 'senia_free'] )
    # crawl_proc.crawl(HhunterSpider)
    crawl_proc.start()
    print(next_level)
