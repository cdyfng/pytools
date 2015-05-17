from flask import Flask, request
import os

app = Flask(__name__)
import ConfigParser
import smtplib, string
config = ConfigParser.ConfigParser()
cur_dir =  os.path.dirname(os.path.abspath(__file__))
config.readfp(open(cur_dir + "/myconfig.ini","rb"))

def get_last_ip():
    return config.get("global","lastip")

def save_current_ip(cur_ip):
    config.set("global", "lastip", cur_ip)
    config.write(open("myconfig.ini", "w"))

@app.route('/')
def hello():
    text = request.args.get('text')
    return 'hello %s' % text


@app.route('/dynamicIp', methods=['GET', 'POST'])
def dynamicIp():
    if request.method == 'POST':
        return 'Post return None'
    else:
        setip = request.args.get('setip')
        if setip == None:
            return '{"ip":"%s"}' % get_last_ip()
        else:
            save_current_ip(setip)
            return '{"ip":"%s"}' % setip

#http://192.168.1.113:5000/dynamicIp?setip=112.112.112.112
#http://192.168.1.113:5000/dynamicIp
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
