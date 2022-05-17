from multiprocessing import Pool, Manager
import time
import os
import random
from collector.collector import NewsCollector

done_tasks = list()
def task(x, procs):
    print(f"PID = {os.getpid()} started")
    procs[os.getpid()] = True
    time.sleep(random.randint(2, 5))
    procs[os.getpid()] = False
    return 'OK'

def task_done(result):
    print(f"PID = {os.getpid()} is done")
    done_tasks.append(result)

def _start_scraper(news_collector):
    pool_data = [ 
        news_collector.get_cnn_spider_data('apple', 'business', start_date = 'today', days_from_start_date=5), 
        news_collector.get_cnn_spider_data('tesla', 'business', start_date = 'today', days_from_start_date=5), 
    ]

    with Pool() as pool:
        res = pool.map(news_collector.start_cnn_search, pool_data)
    
    print(f"Completed processes with code {res}")

if __name__ == '__main__':

    m = Manager()
    procs = m.dict()

    pool = Pool()
    collector = NewsCollector()

    _start_scraper(collector)

    # for x in range(10):
    #     pool.apply_async(task, args = (x, procs), callback = task_done )

    # while len(done_tasks) < 10:
    #     pids = [pid for pid, running in procs.items() if running]
    #     print('running jobs: ', pids)
    #     time.sleep(1)
    
    # print(done_tasks)

    # pool.close()
    

