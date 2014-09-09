#!/usr/bin/env python
#-*- coding: utf-8 -*-
#通过urllib(2)模块下载网络内容
import urllib,urllib2,gevent
#引入正则表达式模块，时间模块
import re,time,random
from gevent import monkey
   
monkey.patch_all()

def getlist(i):
    print 'getlist in[%d]' % i
    time.sleep(1)
    print 'getlist out[%d]' % i
    return range(5)


def download(i, j):
    print 'download in[%d, %d]' % (i, j)
    time.sleep(random.randint(0, 100) * 0.05)
    print 'download out[%d, %d]' % (i, j)

 
if __name__ == '__main__':
    jobs = []
    #进行图片下载
    for i in range(10):
        print 'main loop %d' % i
        for j in getlist(i):
            #jobs.append(gevent.spawn(download, i, j))
            download(i ,j)            
    print 'main joinall '
    #gevent.joinall(jobs)
