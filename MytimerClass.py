#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import time



class timer(threading.Thread):
    def __init__(self, num, intervals):
        threading.Thread.__init__(self)
        self.thread_num = num
        self.intervals = intervals
        self.thread_stop = False
        #read config

    def run(self):
        while not self.thread_stop:
            print 'Thread Object(%d), Time:%s\n' %(self.thread_num, time.ctime())  
            time.sleep(self.intervals)

    def stop(self):
        self.thread_stop = True


if __name__ == '__main__': 
    t1 = timer(1, 5)
    t2 = timer(2, 20)
    t1.start()
    t2.start()
    while True:
        time.sleep(1)







def main_process():
    #compare price 
    #trading
    pass


 
def timer_start():
    t = threading.Timer(5,test_func,("msg1","msg2"))
    t.start()
 
def test_func(msg1,msg2):
    print "I'm test_func,",time.strftime('%Y-%m-%d %H:%M:%S'),msg2
    timer_start()
    main_process()    
 
if __name__ == "__main__":
    timer_start()
    while True:
        time.sleep(1)

