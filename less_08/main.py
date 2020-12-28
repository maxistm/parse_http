from scrapy.crawler import CrawlerProcess, CrawlerRunner
from scrapy.settings import Settings
from gb_parse.spiders.instagramchain import InstagramChainSpider
import dotenv
import os
from twisted.internet import reactor
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue


# def double_link(user):
#     frends = []
#     for follow in user['follow']:
#         if follow in user['followers']:
#             frends.append(follow)
#     return frends

#синхронно не работает
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
    

# def f(q, frends):
#     try:
#         user = []
#         user.append(frends)
#         crawl_settings = Settings()
#         crawl_settings.setmodule('gb_parse.settings')
#         next_level = {}
#         runner = CrawlerRunner(settings=crawl_settings)
#         deferred = runner.crawl(InstagramChainSpider,  login=os.getenv('LOGIN'),
#                 enc_password=os.getenv('PASSWORD'), next_level = next_level, users = user)
#         deferred.addBoth(lambda _: reactor.stop())
#         reactor.run()
#         q.put(next_level)
#     except Exception as e:
#         q.put(e)
#  # the wrapper to make it run more times
# def get_frends(users, frends):
#     users[frends] = []
#     q = Queue()
#     p = Process(target=f, args=(q,frends))
#     p.start()
#     next_level = q.get()
#     p.join()
#         #d.addBoth(lambda _: l.start(0, False))
#     for key, value in next_level.items():
#         users[key] = double_link(value)

#     #l = task.LoopingCall(run_spider2)
#     #l.start(0)

#     #reactor.run()

# def bfs(s, t):
#     path = []
#     # s - начальная вершина
#     # t - пункт назначения
#     users = {}
#     # инициализируем очередь
#     queue=[]
#     # добавляем s в очередь

#     queue.append(s)
#     # помечаем s как посещенную вершину во избежание повторного добавления в очередь
  
#     visited_users.append(s)
#     get_frends(users, s)
#     #get_next_freinds(users, frends)

#     while len(queue) > 0:
#         # удаляем первый (верхний) элемент из очереди
#         v = queue.pop(0) 
#         path.append(v)
#         if v not in users:
#             get_frends(users, v)
#         for friend in users[v]:
#             # если friend не посещался
#             if friend not in visited_users:
#                 # добавляем его в очередь
#                 queue.append(friend)
#                 # помечаем вершину как посещенную
#                 visited_users.append(friend)
                
#                 # если friend является пунктом назначения, мы победили
#                 if friend == t: 
#                     path.append(friend)
#                     return True, path
#         #get_frends(users, users[v])
#         #get_next_freinds(users, users[v])        

#     # если t не обнаружено, значит пункта назначения достичь невозможно
#     return False

dotenv.load_dotenv()
visited_users = []
if __name__ == '__main__':
    query = ['trillij', 'pshigoda']
    configure_logging()
    get_next_freinds(query)
    #result, quere = bfs('maxisfx', 'trillij')
    print(query)
