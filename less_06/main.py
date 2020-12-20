from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.instagram import InstagramSpider
import dotenv
import os

# from gb_parse import settings
dotenv.load_dotenv()
if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(InstagramSpider, login=os.getenv('LOGIN'),
                     enc_password=os.getenv('PASSWORD'), tag_list=['python', ])
    # crawl_proc.crawl(HhunterSpider)
    crawl_proc.start()
