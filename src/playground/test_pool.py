from multiprocessing import Pool
import time
import os
import random

done_tasks = list()
def task(x):
    print(f"PID = {os.getpid()} started")
    time.sleep(random.randint(2, 5))
    return 'OK'

def task_done(result):
    print(f"PID = {os.getpid()} is done")
    done_tasks.append(result)

def _start_scraper():
    print("_start_scraper starts")
    pool = Pool() 

    for i in range(10):
        pool.apply_async(task, (i, ), callback = task_done)

    pool.close()
    print("_start_scraper ends")

if __name__ == '__main__':

    # m = Manager()
    # procs = m.dict()

    print("start")
    pool = Pool() 

    for i in range(10):
        pool.apply_async(task, (i, ), callback = task_done)

    pool.close()
    pool.join()
    print("ends")

    # for x in range(10):
    #     pool.apply_async(task, args = (x, procs), callback = task_done )

    # while len(done_tasks) < 10:
    #     pids = [pid for pid, running in procs.items() if running]
    #     print('running jobs: ', pids)
    #     time.sleep(1)
    
    # print(done_tasks)

    # pool.close()
    

