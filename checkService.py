#!/usr/bin/env python
# name IsOpen.py
import os, subprocess
import socket
def IsOpen(ip,port):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        s.connect((ip,int(port)))
        s.shutdown(2)
        print '%d is open' % port
        return True
    except:
        print '%d is down' % port
        return False

def runPyService(pyname):
    INTERPRETER = "/usr/bin/python"
    if not os.path.exists(INTERPRETER): 
        print "Cannot find INTERPRETER at path \"%s\"." % INTERPRETER
    processor = pyname
  
    pargs = [INTERPRETER, processor] 
    pargs.extend(["--input=inputMd5s"]) 
    subprocess.Popen(pargs) 


if __name__ == '__main__':
    if IsOpen('127.0.0.1',8000) != True:
        runPyService(os.path.dirname(os.path.abspath(__file__)) + '/yourpyfile.py')

    

