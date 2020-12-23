from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_parse.spiders.hhunter import HhunterSpider


# from gb_parse import settings

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_parse.settings')
    # crawl_settings.setmodule(settings)
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(HhunterSpider)
    crawl_proc.start()
