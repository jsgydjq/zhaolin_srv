import urllib2, sys
from threading import Thread,Lock
from Queue import Queue
import time
import random
import worker_game

class Fetcher:
    def __init__(self,threads):
        self.opener = urllib2.build_opener(urllib2.HTTPHandler)
        self.lock = Lock() #thread locker
        self.q_req = Queue() #todo queue
        self.q_ans = Queue() #done queue
        self.threads = threads                                      
        for i in range(threads):
            t = Thread(target=self.threadget)
            t.setDaemon(True)
            t.start()                          
        self.running = 0
		
    def __del__(self): #wait for both the queues finished
        time.sleep(0.5)
        self.q_req.join()  
        self.q_ans.join()
		
    def taskleft(self):
        return self.q_req.qsize()+self.q_ans.qsize()+self.running
		
    def push(self,req):
        self.q_req.put(req)
		
    def pop(self):
        return self.q_ans.get()

    def threadget(self):
        while True:
            req = self.q_req.get()    
            with self.lock: #get into critical area
                self.running += 1
            try:
                content = self.opener.open(req).read()
                type = sys.getfilesystemencoding()
                ans = unicode(content, 'utf-8')

            except Exception, what:
                ans = ''
                print what
            self.q_ans.put((req,ans))
            with self.lock:
                self.running -= 1
            self.q_req.task_done()  
            time.sleep(random.uniform(0.5, 3)) # don't spam

def start():
    links = ['http://www.anzhi.com/sort_2_%d_hot.html' %i for i in range(0, 2888)]

    f = Fetcher(threads=10)
    for url in links:
        f.push(url)
    while f.taskleft():
        url,content = f.pop() 
        th = Thread(target=worker_game.analyze(content))
        th.setDaemon(True)
        th.start() 
