#!/usr/bin/python
# -*- coding: utf-8 -
import time,datetime,threading,os,sqlite3
import re
from bs4 import BeautifulSoup
from httpGet import httpGetContent
from common import decimal, validate_decimal, str_to_date
import urllib2
import warningEmail

#stocks = {
#    'sh600999': 0.02,
#    'sh600036': 0.01,
#    'sh600050': 0.02,
#    'sh600718': 0.02,
#    'sh601857': 0.02,
#    'sz002230': 0.02,
#    }


DATA_DIR = './data/air/'
DB_NAME = 'chn.db'
NOW_PRICE_SQL = "select timestamp, now_price, yesterday_closing_price from '_TABLENAME_' where  stock_id = '_STOCKID_'  order by id desc limit 1"

class Stock(threading.Thread):
    def __init__(self, stock_id, price_interval_percent, base_price, bench_price):
        threading.Thread.__init__(self)
        self.stock_id = stock_id
        self.price_interval_percent = price_interval_percent
        self.price_threshold_low = 0.0
        self.price_threshold_high = 0.0
        self.base_price = base_price
        self.bench_price = bench_price
        self.is_stop = False
        pass
    def run(self):
        while (not self.is_stop):
            if(not is_trade_time()):
                print get_beijing_time().strftime('%H:%M:%S'), 'not trade time'
                time.sleep(120)
                continue

            try:
                price,_ = self.getLastPrice()
            except Exception, e:
                price,_ = -1, -1
                print e
                time.sleep(5)
            if price != -1 and price !=0 :
                if self.price_threshold_low == 0:
                    threshold_unit = self.base_price * self.price_interval_percent
                    self.price_threshold_low = self.base_price - threshold_unit 
                    self.price_threshold_high = self.base_price + threshold_unit 
                    print 'init %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                if price >= self.price_threshold_high:
                    threshold_unit = self.base_price * self.price_interval_percent
                    self.price_threshold_high += threshold_unit
                    self.price_threshold_low += threshold_unit
                    self.base_price += threshold_unit
                    print 'high notify %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                    subject = self.stock_id + ' high ' + str(self.price_interval_percent)
                    content = 'now: %.2f bench: %.2f rate: %.2f' \
                        %(price, self.bench_price, \
                        (price - self.bench_price)/self.bench_price * 100.0)
                    print subject + '\n' + content
                    self.emailNotify(subject, content)

                if price <= self.price_threshold_low:
                    threshold_unit = self.base_price * self.price_interval_percent
                    self.price_threshold_high -= threshold_unit
                    self.price_threshold_low -= threshold_unit
                    self.base_price -= threshold_unit
                    print 'low notify %f %f %f'%(threshold_unit, self.price_threshold_low, self.price_threshold_high )
                    subject = self.stock_id + ' low ' + str(self.price_interval_percent)
                    content = 'now: %.2f bench: %.2f rate: %.2f' \
                        %(price, self.bench_price, \
                        (price - self.bench_price)/self.bench_price *100.0 )
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
        wemail = warningEmail.warningEmail()
        wemail.send(subject, content)
        self.saveConfig()

 
    def saveConfig(self):        
        stocks =  readStocks()
        for stock in stocks:
            if stock[0] == self.stock_id :
                stock[2] = self.base_price
                print '%s %f %f changed'%(stock[0],stock[1],stock[2])
        saveStocks(stocks)
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
    #return True
    dbtime = datetime.datetime.strptime(str_time,'%Y-%m-%d %H:%M:%S')
    now = get_beijing_time()
    delta = (now - dbtime).seconds
    #两分钟内数据视为当前数据
    if delta > 120:
        print 'delta:', delta
        return False
    return True

cur_dir =  os.path.dirname(os.path.abspath(__file__))

def readStocks():
    listStocks = []
    stockRe = re.compile('(.*),(.*),(.*),(.*),(.*),(.*)')
    for line in open(cur_dir + '/config.ini').readlines():
        line = line.strip()
        m = stockRe.search(line)
        if m:
                stockId, percent, startPrice, \
                    lowNotifyPrice, highNotifyPrice, benchPrice \
                    = m.groups()
                #print stockId, startPrice, percent, \
                #    lowNotifyPirce, highNotifyPrice, nowPrice
                listStocks.append([str(stockId),float(percent),float(startPrice), \
                    float(lowNotifyPrice), float(highNotifyPrice), float(benchPrice)])
    return listStocks

def saveStocks(listStocks):
    stockconfig = open(cur_dir + '/config.ini','wt')
    for stock in listStocks:
        w=str(stock[0])+','+str(stock[1]) + ','+str(stock[2]) \
             + ','+str(stock[3]) + ','+str(stock[4]) + ','+str(stock[5])
        stockconfig.write(w)
        stockconfig.write('\n')
    stockconfig.close



def stock_base_info(code):
    """
    得到股票其他的基础数据信息
    包含：
    pe_trands 市盈率（动态）：47.98
    type 分类 ：big（大盘股）medium （中盘股）small（小盘股）
    pe_static 市盈率（静态）：8.61
    total_capital 总股本 44.7亿股
    ciculate_capital 流通股本 44.7亿股
    pb 市净率 1.24

    """
    url = "http://basic.10jqka.com.cn/%s/" % code
    content = httpGetContent(url)
    if content:
        stock_dict = {}
        soup = BeautifulSoup(content)
        profile = soup.select('div#profile')

        table = profile[0].select('table')[0]
        td_list = table.select('td')
        td_select_key = lambda td: td.select('span')[0].text.strip().replace('\t','')
        td_select_value = lambda td: td.select('span')[1].text.strip().replace('\t','')
        for i, td in enumerate(td_list):
            #print td_select_key(td), td_select_value(td)
            #stock_dict[td_select_key(td)] = td_select_value(td)
            if i == 0:    # 主营业务：
                stock_dict["main_busyness"] = td_select_value(td)
            elif i == 1:    # 所属行业：
                stock_dict["industry"] = td_select_value(td)
            elif i == 2:    # 涉及概念：
                stock_dict["concept"] = td_select_value(td)
 
        table = profile[0].select('table')[1]
        td_list = table.select('td')
        td_select_key = lambda td: td.select('span')[0].text.strip().replace('\t','')
        #td_select_value = lambda td: td.select('span')[1].text.strip().replace('\t','')
        td_select = lambda td: td.select('span')[1].text.strip().replace('\t','')
        for i, td in enumerate(td_list):
            #print td_select_key(td), td_select_value(td)
            #stock_dict[td_select_key(td)] = td_select_value(td)
            stock_dict["code"] = code
            if i == 0:    # 市盈率(动态)：
                stock_dict["pe_ratio_dynamic"] = validate_decimal(td_select(td))
            elif i == 2:  # 净资产收益率
                stock_dict['return_on_equity'] = validate_decimal(td_select(td))
            elif i == 3:  # 分类
                text = td_select(td)
                if text == u"大盘股":
                    stock_dict['type'] = 'big'
                elif text == u'中盘股':
                    stock_dict['type'] = 'medium'
                elif text == u"小盘股":
                    stock_dict['type'] = 'small'
                else:
                    stock_dict['type'] = text
            elif i == 4:  # 市盈率(静态)
                stock_dict['pe_ratio_static'] = validate_decimal(td_select(td))
            elif i == 5:  # 营业收入
                stock_dict['income'] = validate_decimal(td_select(td))
            elif i == 6:  # 每股净资产
                stock_dict['assert_per_share'] = validate_decimal(td_select(td))
            elif i == 7:  # 总股本
                stock_dict['total_capital'] = validate_decimal(td_select(td))
            elif i == 8:  # 市净率
                stock_dict['pb'] = validate_decimal(td_select(td))
            elif i == 9:  # 净利润
                stock_dict['net_profit'] = validate_decimal(td_select(td))
            elif i == 10:  # 每股现金流 
                stock_dict['cash_flow_per_share'] = validate_decimal(td_select(td))
            elif i == 11: # 流通股本
                stock_dict['circulate_capital'] = validate_decimal(td_select(td))


        #for item in stock_dict:
        #    print item, stock_dict[item]

        return stock_dict


class DailyStat():
    def __init__(self):
        self.code_list = []
        self.code_list.extend(read_code('sz.list2', 'sz'))
        self.code_list.extend(read_code('sh.list2', 'sh'))
        #code_list.extend(read_code('my.list', 'sh'))
        #print self.code_list
        print 'Get', len(self.code_list), 'stock id from lists'
        start = time.time()
        #for stock_id in self.code_list:
        #    self.stock_id = stock_id
        #    try:
        #        price,yesterday_closing_price = self.getLastPrice()
        #    except Exception, e:
        #        price,yesterday_closing_price = -1, -1
        #        print e
        #    print self.stock_id, price, yesterday_closing_price 
        stocks =[]
        for p in self.getLastPrice():
            #print p
            riseFallRate = (p[1] - p[2]) / p[2]
            #print p, riseFallRate 

            if p[1] != 0 and p[2] !=0 and (riseFallRate > 0.1 or riseFallRate < -0.1):
                #print p[0], riseFallRate
                stocks.append((p[0],p[1],p[2],riseFallRate))

        print '------------------------------'
        for stock in stocks:
            print stock
            print time.time() - start
            #stock[0] 'sh600001'
            #stock[0][2:] '600001'
            info = stock_base_info(stock[0][2:])
            #print stock
        
        print time.time() - start

        #取得所有股票代码以及名称
        #self.stocks
        #self.stocks_rise_10percents
        #self.stocks_fall_10percents
        pass

    def getDetails(self):
        pass

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
        #table_name = 'table20141226'
        for stock_id in self.code_list:
            #print stock_id
            select = NOW_PRICE_SQL.replace('_TABLENAME_', table_name)
            select = select.replace('_STOCKID_', stock_id)
            #print select
            self.cursor.execute(select)
            res = self.cursor.fetchall()
            try:
                yield (stock_id, res[0][1], res[0][2])
            except Exception as e:
                print e
        #recent_price = res[0]
        #print res[0][0]
        #print res[0][1]
        self.cursor.close()
        self.conn.close()
        #if not is_now_time(res[0][0]):
        #    return -1, -1
        #return res[0][1], res[0][2] #recent_price[1]

    def emailNotify(self, subject, content):
        import warningEmail
        wemail = warningEmail.warningEmail()
        wemail.send(subject, content)
        self.saveConfig()


#API
TOT_PARAMS = 33
def data_parser(data):
    """
    return a dict:
    key is a tuple (stock_id, date, time)
    value is a tuple contains parameters in the following order
    (
        open_price, yesterday_closing_price,
        now_price, high_price, low_price,
        now_buy_price, now_sell_price, #same as buy_1_price and sell_1_price
        volume, amount,
        buy_1_vol, buy_1_price,
        buy_2_vol, buy_2_price,
        buy_3_vol, buy_3_price,
        buy_4_vol, buy_4_price,
        buy_5_vol, buy_5_price,
        sell_1_vol, sell_1_price,
        sell_2_vol, sell_2_price,
        sell_3_vol, sell_3_price,
        sell_4_vol, sell_4_price,
        sell_5_vol, sell_5_price
    )
    """
    global TOT_PARAMS
    ret = dict()
    lines = data.split('\n')
    for line in lines:

        eq_pos = line.find('=')
        if eq_pos == -1:
            continue

        params_seg = line[eq_pos + 2:-1]
        params = params_seg.split(',')
        if len(params) != TOT_PARAMS:
            continue

        stock_id_seg = line[:eq_pos]
        stock_id = stock_id_seg[stock_id_seg.rfind('_') + 1:]
        date = params[30]
        time = params[31]
        #params[32] is nothing


        key = (stock_id, date, time)

        value = tuple(params[0:30])

        ret[key] = value
    return ret

PAGESIZE = 700
WEB_TIME_OUT = 5
DM_TIME_OUT = 10

def stock_crawler():
    code_list = []
    code_list.extend(read_code('sz.list', 'sz'))
    code_list.extend(read_code('sh.list', 'sh'))


    stocks =[]
    for start_id in range(0, len(code_list), PAGESIZE):
        end_id = min(start_id + PAGESIZE, len(code_list))
        sub_list = code_list[start_id : end_id]
        #sub_task_name = 'sub_task' + str(cnt) + '[' + str(start_id) + ',' + str(end_id - 1) + ']'
        #sub_task = sub_crawler(sub_task_name, sub_list, io_queue)
    
        code_join = ','.join(sub_list)
        content = ''
        try:
            print 'get content'
            #sta = time.time()
            content = urllib2.urlopen('http://hq.sinajs.cn/list=' + code_join, None, WEB_TIME_OUT).read()
            #end = time.time()
            #print end - sta
            print len(content)
        except:
            print self.name, 'Network Timeout! Now try again ...', time.ctime()
            #good = False
            #if not good:
            #continue
        data = data_parser(content)
        

        #print data
        for (stockId, d, t) in data:
            yesterday_closing_price = float(data[stockId,d,t][2])
            now_price =  float(data[stockId,d,t][3])
            try:    
                riseFallRate = (now_price - yesterday_closing_price) / yesterday_closing_price
            #print riseFallRate
            except Exception as e:
                riseFallRate = 0
                print e 
            #    pass
            #print stockId, now_price, yesterday_closing_price, riseFallRate
            if now_price != 0 and yesterday_closing_price !=0 \
                and (riseFallRate > 0.1 or riseFallRate < -0.1):
                stocks.append((stockId,data[stockId,d,t][0],now_price,yesterday_closing_price,riseFallRate))
            

    #print stocks
    sortStocks = sorted(stocks, key = lambda s: s[4], reverse = True)

    emailContent = ''
    #file = open('info.txt','w')
    for stock in sortStocks:
        #print stock[0], stock[1].decode('gbk'), stock[2], stock[3], stock[4]
        try: 
            seprator = '-' * 40
            info = stock_base_info(stock[0][2:])
            strInfo = '%s %s %s %.2f(tl) %.2f(p) %.2f(rf) %.2f(d) %.2f(s) %.2f(pb) %.2f \n%s |%s \n%s \n%s\n' %(info['code'], stock[1].decode('gbk').encode('utf-8'), info['type'], info['total_capital']* stock[2], stock[2], stock[4], \
               info['pe_ratio_static'], info['pe_ratio_dynamic'], info['pb'], info['income'], \
               info['industry'].encode('utf-8'), info['main_busyness'].encode('utf-8'),
               info['concept'].encode('utf-8'), seprator)
            print strInfo
            #print '---------------------------------------------------'
            
        except Exception as e:
            info = {}
            print stock
            print e

        emailContent += strInfo
        #emailContent = u''.join((emailContent, strInfo)).encode('utf-8').strip()

    wemail = warningEmail.warningEmail()
    wemail.send('daily report', emailContent)
 
        #file.write(str(stock))

    #file.close()
        
            
            
            
        #print data
     


def read_code(file_name, prefix):
    code_file = open(file_name)
    ret = []
    for code in code_file:
        code = code.strip()
        ret.append(prefix + code)
    return ret


def remindPrice():
    stocks = readStocks()
    print stocks
    for stock in stocks:
        #print stock[0], stock[1], stock[2]
        t = Stock(stock[0], stock[1], stock[2], stock[5])
        t.start()

    print 'notify already start ...'

def dailyStatAndRemind():
    ds = DailyStat()
    



    
if __name__ == '__main__':

    remindPrice() 
    #dailyStatAndRemind()
    #tstart = time.time()
    #stock = ['600170',u'上海建工'.encode('gbk'),8.64, 8.42, 0.1]
    #info = stock_base_info('600170')
    #600xxx 赤生化 small 市值 股价 静态市盈率 动态市盈率 pb 收入
    #行业| 主营业务
    #概念
    #strInfo = '%s %s %s %.2f %.2f %.2f(d) %.2f(s) %.2f(pb) %.2f \n%s |%s \n%s' %(info['code'], stock[1].decode('gbk'), info['type'], info['total_capital']* stock[2], stock[2], \
    #           info['pe_ratio_static'], info['pe_ratio_dynamic'], info['pb'], info['income'], \
    #           info['industry'], info['main_busyness'],
    #           info['concept'] )
    #print strInfo
    #print time.time() - tstart
    #print info

    #while True:
    #   time.sleep(1)
    #stock_crawler()
