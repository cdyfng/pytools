#!/usr/bin/env python
import sys,os,time
import tornado.httpserver
import tornado.ioloop
import tornado.web
global cnt 
cnt = 0
cur_dir =  os.path.dirname(os.path.abspath(__file__))
file_out = open(cur_dir + '/tanado.log','a')
seprate = ' '
class ServeHTTP(tornado.web.RequestHandler):
    def get(self, txt, num):
        global cnt
        cnt = cnt + 1
        log_str = ''.join([time.ctime()[4: -5], txt, seprate,  str(num), seprate, str(cnt), '\n'])
        file_out.write(log_str)
        #print txt,num,cnt 
        for i in xrange(int(num)):
            self.write("%d: %s\n" % (i, txt))


urls = [
    ("^/([^/]+)/([0-9]+)$", ServeHTTP)
]
app = tornado.web.Application(urls)

if __name__ == "__main__":
    server = tornado.httpserver.HTTPServer(app)
    server.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.instance().start()
