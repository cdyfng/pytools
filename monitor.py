#!/usr/bin/env python
import inspect
import time, os
import json
import socket
import psutil
#import MySQLdb

#db = MySQLdb.connect(user="root", passwd="", \
#                   db="monitor", charset="utf8")
#db.autocommit(True)
#c = db.cursor()

import sqlite3

con = sqlite3.connect('monitor.db3')
c = con.cursor()
#CREATE TABLE stat(id INTEGER PRIMARY KEY AUTOINCREMENT,
#host TEXT, mem_free INTEGER, mem_usage INTEGER,
#mem_total INTEGER, load_avg TEXT, time INTEGER,
#cpu_usage REAL DEFAULT(0.0), disk_usage REAL DEFAULT(0.0),
#unique(id));
class mon:
    def __init__(self):
        self.data = {}

    def getTime(self):
        return str(int(time.time()) + 8 * 3600)

    def getHost(self):
        return socket.gethostname()

    def getLoadAvg(self):
        with open('/proc/loadavg') as load_open:
            a = load_open.read().split()[:3]
            return ','.join(a)

    def getMemTotal(self):
        with open('/proc/meminfo') as mem_open:
            a = int(mem_open.readline().split()[1])
            return a / 1024

    def getMemUsage(self, noBufferCache=True):
        if noBufferCache:
            with open('/proc/meminfo') as mem_open:
                T = int(mem_open.readline().split()[1])
                F = int(mem_open.readline().split()[1])
                B = int(mem_open.readline().split()[1])
                C = int(mem_open.readline().split()[1])
                return (T-F-B-C)/1024
        else:
            with open('/proc/meminfo') as mem_open:
                a = int(mem_open.readline().split()[1]) - int(mem_open.readline().split()[1])
                return a / 1024

    def getMemFree(self, noBufferCache=True):
        if noBufferCache:
            with open('/proc/meminfo') as mem_open:
                T = int(mem_open.readline().split()[1])
                F = int(mem_open.readline().split()[1])
                B = int(mem_open.readline().split()[1])
                C = int(mem_open.readline().split()[1])
                return (F+B+C)/1024
        else:
            with open('/proc/meminfo') as mem_open:
                mem_open.readline()
                a = int(mem_open.readline().split()[1])
                return a / 1024

    def getCpuUsage(self):
        return psutil.cpu_percent(interval=1)
    def getDiskUsage(self):
        return float(os.popen('df|grep rootfs|awk \'{print $5}\'')\
                     .read().split('%')[0])

    def runAllGet(self):
        for fun in inspect.getmembers(self, predicate=inspect.ismethod):
            if fun[0][:3] == 'get':
                self.data[fun[0][3:]] = fun[1]()
        return self.data

    def insertMysql(self):
        data = self.runAllGet()
        #try:
        #    sql = "INSERT INTO `stat` \
        #        (`host`,`mem_free`,`mem_usage`,\
        #        `mem_total`,`load_avg`,`time`) \
        #        VALUES('%s', '%d', '%d', '%d', '%s', '%d')" \
        #        % (data['Host'], data['MemFree'], data['MemUsage'],\
        #           data['MemTotal'], data['LoadAvg'], int(data['Time']))
        #    ret = c.execute(sql)
        #except MySQLdb.IntegrityError:
        #    pass

    def insertSqlite(self):
        data = self.runAllGet()
        sql = "INSERT INTO `stat` \
            (`host`,`mem_free`,`mem_usage`,\
            `mem_total`,`load_avg`,`time`,`cpu_usage`, `disk_usage`) \
            VALUES('%s', '%d', '%d', '%d', '%s', '%d' ,'%f', '%f')" \
            % (data['Host'], data['MemFree'], data['MemUsage'],\
            data['MemTotal'], data['LoadAvg'], int(data['Time']),\
            data['CpuUsage'],data['MemUsage'])
        print data['CpuUsage'], data['DiskUsage']
        try:
            c.execute(sql)
            con.commit()
        except Exception as e:
            print e


if __name__ == "__main__":
    myMon = mon()
    #myMon.runAllGet()
    #myMon.insertMysql()
    #for i in range(100):
    while True:
        myMon.insertSqlite()
        time.sleep(30)
        print ".."
    pass
    #while True:
    #    m = mon()
    #    data = m.runAllGet()
    #    print data
    #    req = urllib2.Request("http://51reboot.com:8888", json.dumps(data), {'Content-Type': 'application/json'})
    #    f = urllib2.urlopen(req)
    #    response = f.read()
    #    print response
    #    f.close()
    #    time.sleep(60)
