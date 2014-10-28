#!/usr/bin/python
#-*- coding: utf-8 -*-

import re, urllib2, os, time
import ConfigParser
import smtplib, string
config = ConfigParser.ConfigParser()
config.readfp(open("myconfig.ini","rb"))
cur_dir =  os.path.dirname(os.path.abspath(__file__))

def getProvinceWeb(telNumber):
    strZoneResult = urllib2.urlopen("http://tcc.taobao.com/cc/json/mobile_tel_segment.htm?tel=" + telNumber).read().decode('gbk').encode('utf-8')
    print strZoneResult
    pattenPreNum =  u'mts:\'(.*?)\''
    pattenProvince =  u'province:\'(.*?)\''
    matchPreNum  = re.search(pattenPreNum, strZoneResult)
    preNum = matchPreNum.group(1) if matchPreNum else '0000000'

    matchProvince  = re.search(pattenProvince, strZoneResult)
    province = matchProvince.group(1) if matchProvince else u'错误省份结果'

    return preNum, province

numsDbRe =  re.compile('(^1[0-9]{6}),(.*)')
#numsDB = loadRegion()

def loadRegion():
    RegionDb = {}
    try:
        for line in open(cur_dir + '/num_province_db').readlines():
            line = line.strip()
            m = numsDbRe.search(line)
            if m:
                nums,area = m.groups()
                RegionDb[nums] = area
        return RegionDb
    except Exception,e:
        print e
        return {}

       
def NewRegionSave(numPre, province):
    file_out = open(cur_dir + '/num_province_db', 'a')
    file_out.write(''.join([numPre, ',', province, '\r\n']))
    file_out.flush()
    file_out.close()

def getRegion(number,numsDb):
    k = number[0:7]
    if not k in numsDb:
        #get from web then update dic and save
        numPre, province = getProvinceWeb(number)
        if numPre != '0000000':
            NewRegionSave(numPre, province)
            numsDb[numPre] = province
            return  numPre, province, 'web_ok'
        return numPre, province, 'web_fail'
    else:
        region = numsDb[k]
        return k, region, 'db_ok'



def get_ip():
    return re.search('\d+\.\d+\.\d+\.\d+', urllib2.urlopen("http://www.whereismyip.com").read()).group(0)

def get_last_ip():
    return config.get("global","lastip")

def save_current_ip(cur_ip):
    config.set("global", "lastip", cur_ip)
    config.write(open("myconfig.ini", "w"))

class myemail():
    def __init__(self):
        self.host = config.get("email","host")
        self.fromaddr = config.get("email","from")
        self.user = config.get("email","user")
        self.passwd = config.get("email","passwd")
        self.to = config.get("email","to")
        print 'host:%s\nfromaddr:%s\nuser:%s\npasswd:%s\nto:%s\n' \
            % (self.host, self.fromaddr, self.user, \
            self.passwd[0:1] + "***" , self.to)
    def send(self, subject, content):
        text = content
        body = string.join((
            "From: %s" % self.fromaddr,
            "To: %s" % self.to,
            "Subject: %s" % subject ,
            "",
            text
            ), "\r\n")
        server = smtplib.SMTP(self.host)
        server.login(self.user, self.passwd)
        server.sendmail(self.fromaddr, self.to, body)
        server.quit()
         
if __name__ == '__main__':
    numsDB = loadRegion()
    for i in range(10000):
        num = 1300000 + i 
        numpre,province,status = getRegion(str(num)+ '1234', numsDB)
        #time.sleep(0.2) 
        print i, num ,province
        

if __name__ == '__main2__':
    cur_ip = get_ip()
    last_ip = get_last_ip()
    print ''.join('current ip is %s' % cur_ip)
    print ''.join('last ip is %s' % last_ip)
    if cmp(cur_ip, last_ip) != 0:
        print 'save new ip and send email'
        save_current_ip(cur_ip)
        #send warnning email
        m = myemail()
        m.send("ip changed", cur_ip)




