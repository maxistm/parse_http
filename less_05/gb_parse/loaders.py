import re
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose
from .items import AutoYoulaItem, HhunterVacancyItem, HhunterCompanyItem


def get_autor(js_string):
    re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_str, js_string)
    return f'https://youla.ru/user/{result[0]}' if result else None


def get_specifications(itm):
    tag = Selector(text=itm)
    result = {tag.css('.AdvertSpecs_label__2JHnS::text').get(): tag.css(
        '.AdvertSpecs_data__xK2Qx::text').get() or tag.css('a::text').get()}
    return result


def specifications_out(data: list):
    result = {}
    for itm in data:
        result.update(itm)
    return result



class AutoYoulaLoader(ItemLoader):
    default_item_class = AutoYoulaItem
    title_out = TakeFirst()
    url_out = TakeFirst()
    description_out = TakeFirst()
    autor_in = MapCompose(get_autor)
    autor_out = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = specifications_out

def salary_out(data):
    return ''.join(data).replace('\xa0',' ')

def description_out(data):
    return ' '.join(data).replace('\xa0',' ') 

def descriptionv_out(data):
    return ' '.join(data).replace('\xa0',' ')  

def skills_out(data):

    return data


class HhunterVacancyLoader(ItemLoader):
    default_item_class = HhunterVacancyItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_out = salary_out
    description_out = description_out
    skills_out = skills_out


class HhunterCompanyLoader(ItemLoader):
    default_item_class = HhunterCompanyItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    official_url_out = TakeFirst()
    description_out = descriptionv_out
    vacancies_out = skills_out
