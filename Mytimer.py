#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading
import time


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

