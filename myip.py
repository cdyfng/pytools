#!/usr/bin/python
#-*- coding: utf-8 -*-

import re, urllib2
import ConfigParser
import smtplib, string
config = ConfigParser.ConfigParser()
config.readfp(open("myconfig.ini","rb"))

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




