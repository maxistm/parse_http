from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.autoyoula import AutoyoulaSpider
import dotenv, os
# from gb_parse import settings

if __name__ == '__main__':
    dotenv_path = os.path.join(os.path.dirname(__file__ ), '.env')
    dotenv.load_dotenv(dotenv_path)
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(AutoyoulaSpider)
    crawl_proc.start()
    