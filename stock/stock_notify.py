#!/usr/bin/python
# -*- coding: utf-8 -
import time,datetime,threading,os,sqlite3

stocks = {
    'sh600999': 0.02,
    'sh600036': 0.01,
    'sh600050': 0.02,
    'sh600718': 0.02,
    'sh601857': 0.02,
    'sz002230': 0.02,
    }


DATA_DIR = './data/air/'
DB_NAME = 'chn.db'
NOW_PRICE_SQL = "select timestamp, now_price, yesterday_closing_price from '_TABLENAME_' where  stock_id = '_STOCKID_'  order by id desc limit 1"

class Stock(threading.Thread):
    def __init__(self, stock_id, price_interval_percent ):
        threading.Thread.__init__(self)
        self.stock_id = stock_id
        self.price_interval_percent = price_interval_percent
        self.price_threshold_low = 0.0
        self.price_threshold_high = 0.0
        self.is_stop = False
        pass
    def run(self):
        while (not self.is_stop):
            if(not is_trade_time()):
                print get_beijing_time().strftime('%H:%M:%S'), 'not trade time'
                time.sleep(120)
                continue

            try:
                price,yes_closing_price = self.getLastPrice()
            except Exception, e:
                price,yes_closing_price = -1, -1
                print e
                time.sleep(5)
            if price != -1 and price !=0 :
                if self.price_threshold_low == 0:
                    threshold_unit = yes_closing_price * self.price_interval_percent
                    self.price_threshold_low = yes_closing_price - threshold_unit 
                    self.price_threshold_high = yes_closing_price + threshold_unit 
                    print 'init %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                if price >= self.price_threshold_high:
                    threshold_unit = yes_closing_price * self.price_interval_percent
                    self.price_threshold_high += threshold_unit
                    self.price_threshold_low += threshold_unit
                    print 'high notify %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                    subject = self.stock_id + ' high ' + str(self.price_interval_percent)
                    content = 'now: %.2f ycp: %.2f rate: %.2f' \
                        %(price, yes_closing_price, \
                        (price - yes_closing_price)/yes_closing_price * 100.0)
                    print subject + '\n' + content
                    self.emailNotify(subject, content)

                if price <= self.price_threshold_low:
                    threshold_unit = yes_closing_price * self.price_interval_percent
                    self.price_threshold_high -= threshold_unit
                    self.price_threshold_low -= threshold_unit
                    print 'low notify %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                    subject = self.stock_id + ' low ' + str(self.price_interval_percent)
                    content = 'now: %.2f ycp: %.2f rate: %.2f' \
                        %(price, yes_closing_price, \
                        (price - yes_closing_price)/yes_closing_price *100.0 )
                    print subject + '\n' + content
                    self.emailNotify(subject, content) 
          
                 
            #比较价格，大道要求则邮件提示
            print get_beijing_time().strftime('%H:%M:%S'), self.stock_id, price
            time.sleep(10)

    def stop(self):
        print 'Try to stop', self.name, '...'
        self.is_stop = True


    def getLastPrice(self):
        file_name = DATA_DIR + '/' + DB_NAME
        ensure_dir(file_name)

        try:
            self.conn = sqlite3.connect(file_name)
            self.cursor = self.conn.cursor()
        except Exception, e:
            print e
            exit()
        current_beijing_date = get_beijing_time().strftime('%Y-%m-%d')
        table_name = 'table' + current_beijing_date.translate(None, '-')
        select = NOW_PRICE_SQL.replace('_TABLENAME_', table_name)
        select = select.replace('_STOCKID_', self.stock_id)
        #print select
        self.cursor.execute(select)
        res = self.cursor.fetchall()
        #recent_price = res[0]
        #print res[0][0]
        #print res[0][1]
        self.cursor.close()
        self.conn.close()
        if not is_now_time(res[0][0]):
            return -1, -1
        return res[0][1], res[0][2] #recent_price[1] 

    def emailNotify(self, subject, content):
        import warningEmail
        wemail = warningEmail.warningEmail()
        wemail.send(subject, content)
        

        #存储提示价格到数据库中
        pass

def ensure_dir(file_name):
    root_dir = os.path.dirname(file_name)
    if root_dir == '':
        root_dir == '.'
    if not os.path.exists(root_dir):
        ensure_dir(root_dir)
        os.makedirs(root_dir)

def get_beijing_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours =+ 8)

def is_trade_time():
    current_beijing_hms = get_beijing_time().strftime('%H:%M:%S')
    if current_beijing_hms < '08:40:00':
        return False
    if current_beijing_hms > '11:50:00' and current_beijing_hms < '12:40:00':
        return False
    if current_beijing_hms > '15:20:00':
        return False
    return True

def is_now_time(str_time):
    dbtime = datetime.datetime.strptime(str_time,'%Y-%m-%d %H:%M:%S')
    now = get_beijing_time()
    delta = (now - dbtime).seconds
    #两分钟内数据视为当前数据
    if delta > 120:
        print 'delta:', delta
        return False
    return True


if __name__ == '__main__':
    for stock in stocks:
        print stock, stocks[stock]
        t = Stock(stock, stocks[stock])
        t.start() 
    
    print 'notify already start ...'  
    
    while True:
       time.sleep(1)

