#!/usr/bin/env python
# name IsOpen.py
import os, subprocess
import time, threading

def runPyService(pyname):
    INTERPRETER = "/usr/bin/python"
    if not os.path.exists(INTERPRETER):
        print "Cannot find INTERPRETER at path \"%s\"." % INTERPRETER
    processor = pyname

    pargs = [INTERPRETER, processor]
    pargs.extend(["--input=inputMd5s"])
    subprocess.Popen(pargs)

def main_process():
    #compare price
    #trading
    try:
        runPyService(os.path.dirname(os.path.abspath(__file__)) \
            + '/metric_distance.py')
    except Exception as e:
        print e
def timer_start():
    t = threading.Timer(10,test_func,("msg1","msg2"))
    t.start()

def test_func(msg1,msg2):
    print "I'm test_func,",time.strftime('%Y-%m-%d %H:%M:%S'),msg2
    timer_start()
    main_process()


if __name__ == '__main__':
    timer_start()
    while True:
        time.sleep(5)


