import bs4
import datetime
import json
import requests
from urllib.parse import urljoin
from database import DataBase


class GbBlogParse:

    def __init__(self, start_url: str, db: DataBase):
        self.start_url = start_url
        self.page_done = set()
        self.db = db

    def __get(self, url) -> bs4.BeautifulSoup:
        response = requests.get(url)
        self.page_done.add(url)
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        return soup

    def run(self, url=None):
        if not url:
            url = self.start_url

        if url not in self.page_done:
            soup = self.__get(url)
            posts, pagination = self.parse(soup)

            for post_url in posts:
                page_data = self.page_parse(self.__get(post_url), post_url)
                self.save(page_data)
            for p_url in pagination:
                self.run(p_url)

    def parse(self, soup):
        ul_pag = soup.find('ul', attrs={'class': 'gb__pagination'})
        paginations = set(
            urljoin(self.start_url, url.get('href')) for url in ul_pag.find_all('a') if url.attrs.get('href'))
        posts = set(
            urljoin(self.start_url, url.get('href')) for url in soup.find_all('a', attrs={'class': 'post-item__title'}))
        return posts, paginations

    def page_parse(self, soup, url) -> dict:

        json_text = soup.find('script', attrs={'type': 'application/ld+json'}).string
        data_dict = json.loads(json_text)
        page_id = soup.find('comments').attrs['commentable-id']
        response_comments = requests.get('https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id='+page_id+'&order=desc')
        
        data = {
            'post_data': {
                'url': url,
                'title': data_dict['headline'],
                'image': data_dict['image']['url'] if 'image' in data_dict else None,
                'date': datetime.datetime.fromisoformat(data_dict['datePublished']) if 'datePublished' in data_dict else None ,
            },
            'writer': {'name': data_dict["author"]['name'],
                       'url': data_dict["author"]['url']},

            'tags': [],
            'comments': self.get_comments(response_comments.json())

        }
        for tag in soup.find_all('a', attrs={'class': "small"}):
            tag_data = {
                'url': urljoin(self.start_url, tag.get('href')),
                'name': tag.text
            }
            data['tags'].append(tag_data)
        
        return data

    def get_comments(self, comments):
        comm = []
        
        for ccc in comments:
            comment = ccc['comment']
            tmp = {
                'author_name': comment['user']['full_name'],
                'id': comment['id'],
                'body': comment['body'],
                'parent_id': comment['parent_id']
            }
            comm.append(tmp)
            if  comment['children']:
                comm.extend(self.get_comments(comment['children']))

            


        return comm
        

    def save(self, page_data: dict):
        self.db.create_post(page_data)


if __name__ == '__main__':
    db = DataBase('sqlite:///gb_blog.db')
    parser = GbBlogParse('https://geekbrains.ru/posts', db)

    parser.run()
