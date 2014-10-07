python 
getimage.py 多线程批量下载图片

geventtest.py 测试gevent用法
pingpong.py pingpong example
myip.py  a python tools to get current ip , if not equal to the saved ip, then send a email to notify user . The myconfig.ini is the config file saved the last ip address and the email information. It test ok from mail.163.com to mail.139.com
webpy.py
 
trnado.py
 $ sudo siege -c 50 -t60S http://ip:port/Hello/10 
 ** SIEGE 3.0.5
 ** Preparing 50 concurrent users for battle.
 The server is now under siege...
 Lifting the server siege...      done.

 Transactions:               2388 hits
 Availability:             100.00 %
 Elapsed time:              59.13 secs
 Data transferred:           0.20 MB
 Response time:              0.72 secs
 Transaction rate:          40.39 trans/sec
 Throughput:             0.00 MB/sec
 Concurrency:               29.26
 Successful transactions:        2388
 Failed transactions:               0
 Longest transaction:           10.79
 Shortest transaction:           0.23


>>> s = open('simple_obj.py').read()
>>> co = compile(s, 'simple_obj.py', 'exec')
>>> import dis
>>> dis.dis(co)
  1           0 LOAD_CONST               0 (1)
              3 STORE_NAME               0 (i)

  2           6 LOAD_CONST               1 ('Python')
              9 STORE_NAME               1 (s)

  3          12 BUILD_MAP                0
             15 STORE_NAME               2 (d)

  4          18 BUILD_LIST               0
             21 STORE_NAME               3 (l)
             24 LOAD_CONST               2 (None)
             27 RETURN_VALUE        

