# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time, os, logging
import getopt, sys


logging.basicConfig(level=logging.DEBUG,\
                   format='%(asctime)s|%(filename)s|%(funcName)s|line:%(lineno)d|%(levelname)s|%(message)s',
                   datefmt='%Y-%m-%d %X',
                   filename=os.path.dirname(os.path.abspath(__file__)) +'/gpio.log'
                   )
def setPinOut(gpio, level):
    GPIO.setmode(GPIO.BOARD)
    #logging.info('set %d to %s'% (gpio, level));
    GPIO.setup(gpio, GPIO.OUT)
    #print type(gpio), type(level)
    if level == 'high':
        GPIO.output(gpio, GPIO.HIGH)
    elif level == 'low':
        GPIO.output(gpio, GPIO.LOW)
    else:
        logging.info('error');

    logging.info('set %d to %s'% (gpio, level));


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hl:i:", ["help", "level=", "ioport="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    ioPort = None
    level = None
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--ioport"):
            ioPort = int(a)
        elif o in ("-l", "--level"):
            level = a
        else:
            assert False, "unhandled option"

    if ioPort != None and level != None:
        setPinOut(ioPort, level)

def usage():
    print 'python x.py -i 18 -l high(low)'

# ...
if __name__ == "__main__":
    main()
