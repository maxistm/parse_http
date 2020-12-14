import re
import scrapy
from ..loaders import HhunterVacancyLoader, HhunterCompanyLoader

class HhunterSpider(scrapy.Spider):
    name = 'hunter'
    db_type = 'MONGO'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/?customDomain=1']
    params = 'search/vacancy?schedule=remote&L_profession_id=0&area=113'
    
    css_query = {
        'vacancies':'div.vacancy-serp div.vacancy-serp-item a.HH-VacancySidebarTrigger-Link',
    }
    
    xpath_query = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
    }
    
    itm_template = {
        'title': '//div[@class="vacancy-title"]/h1/text()',
        'salary': '//p[@class="vacancy-salary"]//text()',
        #'description': '//div[@class="vacancy-description"]/div[@class="bloko-gap bloko-gap_bottom"]//text()',
        'description': 'concat(//div[@class="vacancy-description"]/div[@class="bloko-gap bloko-gap_bottom"]//text(), "\n", //div[@class="g-user-content"]//text())',
        'skills':'//div[@class="bloko-tag-list"]//text()',
        "company_url": '//a[@data-qa="vacancy-company-name"]/@href'
    }

    company_template = {
        'title': '//div[@class="company-header-title-name"]//text()',
        'description': '//div[@class="company-description"]/div[@class="g-user-content"]//text()',
    }
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    
    def parse(self, response):
        yield response.follow('search/vacancy?schedule=remote&L_profession_id=0&area=113', callback = self.vacancies_page_parse)

    def vacancies_page_parse(self, response):
        for pag_page in response.xpath(self.xpath_query['pagination']):
            yield response.follow(pag_page, callback=self.vacancies_page_parse)

        for vacancy in response.css(self.css_query['vacancies']):
            yield response.follow(vacancy.attrib.get('href'), callback=self.vacancy_parse)
        
        

    def vacancy_parse(self, response):
        loader = HhunterVacancyLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.itm_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()
        yield response.follow(response.xpath(self.itm_template['company_url']).get(), callback=self.company_parse)


    def company_parse(self, response):
        loader = HhunterCompanyLoader(response=response)
        loader.add_value('url', response.url)
        for name, selector in self.company_template.items():
            loader.add_xpath(name, selector)
        yield loader.load_item()

         #перебрать вакансии не успел выдаются по запросу в jsonjson
         # hh.ru/shards/employerview/vacancies?page=0&profArea=6&currentEmployerId=3845543&json=true&regionType=OTHER&disableBrowserCache=true

      
  