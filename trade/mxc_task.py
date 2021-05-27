#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import time
import requests
import hmac
import hashlib
from urllib import parse
import sqlite3
from trade.utils import writelog,delete_extra_zero
import datetime



def _get_server_time():
    return int(time.time())


def _sign(API_KEY,SECRET_KEY,method, path, original_params=None):
    params = {
        'api_key': API_KEY,
        'req_time': _get_server_time(),
    }
    if original_params is not None:
        params.update(original_params)
    params_str = '&'.join('{}={}'.format(k, params[k]) for k in sorted(params))
    to_sign = '\n'.join([method, path, params_str])
    params.update({'sign': hmac.new(SECRET_KEY.encode(), to_sign.encode(), hashlib.sha256).hexdigest()})
    return params


def get_symbols(ROOT_URL,API_KEY):
    """获取交易对信息"""
    method = 'GET'
    path = '/open/api/v2/market/symbols'
    url = '{}{}'.format(ROOT_URL, path)
    params = {'api_key': API_KEY}
    response = requests.request(method, url, params=params)
    print(response.json())


def get_rate_limit(ROOT_URL,API_KEY):
    """rate limit"""
    method = 'GET'
    path = '/open/api/v2/common/rate_limit'
    url = '{}{}'.format(ROOT_URL, path)
    params = {'api_key': API_KEY}
    response = requests.request(method, url, params=params)
    print(response.json())


def get_timestamp(ROOT_URL,API_KEY):
    """get current time"""
    method = 'GET'
    path = '/open/api/v2/common/timestamp'
    url = '{}{}'.format(ROOT_URL, path)
    params = {'api_key': API_KEY}
    response = requests.request(method, url, params=params)
    print(response.json())


def get_ticker(ROOT_URL,API_KEY,symbol):
    """get ticker information
    获取Ticker行情"""
    flag = True
    response = ''
    while flag:
        method = 'GET'
        path = '/open/api/v2/market/ticker'
        url = '{}{}'.format(ROOT_URL, path)
        params = {
            'api_key': API_KEY,
            'symbol': symbol,
        }
        response = requests.request(method, url, params=params)
        # print(response.json())
        try:
            print(response.json())
            if str(response.json()['code']) == '200' and len(response.json()['data']) > 0:
                flag = False
        except Exception as e:
            print(e)
    return response.json()


def get_depth(ROOT_URL,API_KEY,symbol, depth):
    """获取深度信息"""
    method = 'GET'
    path = '/open/api/v2/market/depth'
    url = '{}{}'.format(ROOT_URL, path)
    params = {
        'api_key': API_KEY,
        'symbol': symbol,
        'depth': depth,
    }
    response = requests.request(method, url, params=params)
    print(response.json())


def get_deals(ROOT_URL,API_KEY,symbol, limit):
    """get deals records
        获取成交记录"""
    method = 'GET'
    path = '/open/api/v2/market/deals'
    url = '{}{}'.format(ROOT_URL, path)
    params = {
        'api_key': API_KEY,
        'symbol': symbol,
        'limit': limit,
    }
    response = requests.request(method, url, params=params)
    print(response.json())


def get_kline(ROOT_URL,API_KEY,symbol, interval,num=2):
    """k-line data
        获取k线数据"""
    method = 'GET'
    path = '/open/api/v2/market/kline'
    url = '{}{}'.format(ROOT_URL, path)
    params = {
        'api_key': API_KEY,
        'symbol': symbol,
        'interval': interval,
        'limit': num,
    }
    response = requests.request(method, url, params=params)
    print(response.json())
    return response.json()


def get_account_info(ROOT_URL,API_KEY,SECRET_KEY):
    """account information
        获取账户信息"""
    flag = True
    response = ''
    while flag:
        method = 'GET'
        path = '/open/api/v2/account/info'
        url = '{}{}'.format(ROOT_URL, path)
        params = _sign(API_KEY, SECRET_KEY, method, path)
        response = requests.request(method, url, params=params)
        try:
            print(response.json())
            if str(response.json()['code']) == '200' and len(response.json()['data']) > 0:
                flag = False
        except Exception as e:
            print(e)
    return response.json()



def place_order(ROOT_URL,API_KEY,SECRET_KEY,symbol, price, quantity, trade_type, order_type):
    """place order
        下单，容易出现异常。所以用循环来 强制保证"""
    flag = True
    response = ''
    while flag:
        time.sleep(1.0)
        method = 'POST'
        path = '/open/api/v2/order/place'
        url = '{}{}'.format(ROOT_URL, path)
        params = _sign(API_KEY,SECRET_KEY,method, path)
        data = {
            'symbol': symbol,
            'price': price,
            'quantity': quantity,
            'trade_type': trade_type,
            'order_type': order_type,
        }
        print("<===========>下单data",data)
        response = requests.request(method, url, params=params, json=data)
        try:
            print(response.json())
            if str(response.json()['code']) == '200' and len(response.json()['data'])>0:
                flag = False
        except Exception as e:
            print(e)
    return response.json()


def batch_orders(ROOT_URL,API_KEY,SECRET_KEY,orders):
    """batch order
        批量下单
        """
    method = 'POST'
    path = '/open/api/v2/order/place_batch'
    url = '{}{}'.format(ROOT_URL, path)
    params = _sign(API_KEY,SECRET_KEY,method, path)
    response = requests.request(method, url, params=params, json=orders)
    print(response.json())


def cancel_order(ROOT_URL,API_KEY,SECRET_KEY,order_id):
    """cancel in batch
        撤销订单"""
    origin_trade_no = order_id
    if isinstance(order_id, list):
        origin_trade_no = parse.quote(','.join(order_id))
    method = 'DELETE'
    path = '/open/api/v2/order/cancel'
    url = '{}{}'.format(ROOT_URL, path)
    params = _sign(API_KEY,SECRET_KEY,method, path, original_params={'order_ids': origin_trade_no})
    if isinstance(order_id, list):
        params['order_ids'] = ','.join(order_id)
    response = requests.request(method, url, params=params)
    print(response.json())
    return response.json()


def get_open_orders(ROOT_URL,API_KEY,SECRET_KEY,symbol,num=900):
    """current orders
        获取当前挂单"""
    method = 'GET'
    path = '/open/api/v2/order/open_orders'
    original_params = {
        'symbol': symbol,
        'limit':num,
    }
    url = '{}{}'.format(ROOT_URL, path)
    params = _sign(API_KEY,SECRET_KEY,method, path, original_params=original_params)
    response = requests.request(method, url, params=params)
    print(response.json())
    return response.json()


def get_all_orders(ROOT_URL,API_KEY,SECRET_KEY,symbol, trade_type):
    """order list
        所有订单"""
    method = 'GET'
    path = '/open/api/v2/order/list'
    original_params = {
        'symbol': symbol,
        'trade_type': trade_type,
    }
    url = '{}{}'.format(ROOT_URL, path)
    params = _sign(API_KEY,SECRET_KEY,method, path, original_params=original_params)
    response = requests.request(method, url, params=params)
    print(response.json())


def query_order(ROOT_URL,API_KEY,SECRET_KEY,order_id):
    """query order
        查询订单"""
    flag = True
    response = ''
    while flag:
        time.sleep(0.5)
        origin_trade_no = order_id
        if isinstance(order_id, list):
            origin_trade_no = parse.quote(','.join(order_id))
        method = 'GET'
        path = '/open/api/v2/order/query'
        url = '{}{}'.format(ROOT_URL, path)
        original_params = {
            'order_ids': origin_trade_no,
        }
        params = _sign(API_KEY, SECRET_KEY, method, path, original_params=original_params)
        if isinstance(order_id, list):
            params['order_ids'] = ','.join(order_id)
        s = requests.session()
        response = requests.request(method, url, params=params)
        try:
            print(response.json())
            if str(response.json()['code']) == '200' and len(response.json()['data']) > 0:
                flag = False
                s.keep_alive = False
        except Exception as e:
            print(e)

    return response.json()


def handlexception(responsejson):
    '''
    处理异常的返回结果
    :param responsejson:
    :return:
    '''
    code =responsejson['code']
    if(code==429 or code==500):
        print("请求频繁或服务不可用，稍后再试")
        time.sleep(10.0)
    elif(code==200):
        print()


def get_deal_orders(ROOT_URL,API_KEY,SECRET_KEY,symbol):
    """account deal records
        获取成交记录"""
    method = 'GET'
    path = '/open/api/v2/order/deals'
    url = '{}{}'.format(ROOT_URL, path)
    original_params = {
        'symbol': symbol,
    }
    params = _sign(API_KEY,SECRET_KEY,method, path, original_params=original_params)
    response = requests.request(method, url, params=params)
    print(response.json())


def get_deal_detail(ROOT_URL,API_KEY,SECRET_KEY,order_id):
    """deal detail
    获取交易详情"""
    method = 'GET'
    path = '/open/api/v2/order/deal_detail'
    url = '{}{}'.format(ROOT_URL, path)
    original_params = {
        'order_id': order_id,
    }
    params = _sign(API_KEY,SECRET_KEY,method, path, original_params=original_params)
    response = requests.request(method, url, params=params)

    print(response.json())

def CovertTime(timeStamp):
    '''
    时间戳转换成日期
    :param timestamp:
    :return:
    '''
    #timeStamp = 1381419600
    if (len(str(timeStamp))>10):
        timeStamp = float(float(timeStamp) / 1000)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    print(otherStyleTime)  # 2013--10--10 23:40:00
    return otherStyleTime



def connect_db_excute(path,sqlstr):
    '''
    connect db
    :param path:
    :return:
    '''
    conn = sqlite3.connect(path)
    c = conn.cursor()
    print("Opened database successfully")
    c.execute(sqlstr)
    conn.commit()
    print("写入成功！")
    conn.close()

def connect_db_search_all_orders(path,querysql):
    '''
    chaxun dai guance de zhibiao
    :param path:
    :return:
    '''
    conn = sqlite3.connect(path)
    c = conn.cursor()
    print("Opened database successfully")
    cursor=c.execute(querysql)

    scan_order_dic ={}
    for row in cursor:
        scan_order_dic[row[0]] = row[1]
    conn.close()
    if (len(scan_order_dic)>0):
        print("已查询到该用户带扫描的订单号")
        return scan_order_dic
    else:
        print("未查询到该用户需扫描的订单号")



def get_sorted_price_list(ROOT_URL,API_KEY,step_price_list,symbol):
    '''
    获取当前价格在列表价格中的排序
    :return:
    '''
    ##获取当前此刻的价格
    get_ticker_res = get_ticker(ROOT_URL,API_KEY,symbol)
    # get_1m_kline_res = get_kline(symbol, '1m')
    now_time = get_ticker_res['data'][0]["time"]
    now_price = get_ticker_res['data'][0]["last"]
    print("当前的时间是:", CovertTime(now_time), "当前的价格是:", now_price)
    ##将此时的价格插入 列表价格中，排序查看排在第几位
    step_price_list.append(float(now_price))
    sort_step_price_list = (sorted(step_price_list, key=lambda z: float(z)))
    print("排序后等分价格列表：", sort_step_price_list)
    # logstr = "排序后等分价格列表：" + str(sort_step_price_list)
    # writelog(logstr)
    # 找到当前价格的位置
    index = sort_step_price_list.index(float(now_price))
    print(index)
    return sort_step_price_list,index,now_price


def connect_db_search(querysql,path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')):
    '''
    以list的形式返回需要的值
    :param path:
    :return:
    '''
    conn = sqlite3.connect(path)
    c = conn.cursor()
    print("数据库链接成功")
    print(querysql)
    cursor = c.execute(querysql)
    list = []
    columns_tuple = cursor.description
    columns_list = [field_tuple[0] for field_tuple in columns_tuple]
    all = cursor.fetchall()  # 获取所有的值
    conn.close()
    for row in all:
        print(row)
        tempdic = {}
        for i in range(len(columns_list)):
            tempdic[columns_list[i]] = row[i]
        list.append(tempdic)
    return list


def common_buy_order(ROOT_URL,API_KEY,SECRET_KEY,symbol,buyprice,amount,profit_rate,db_path,last_order_id=""):
    '''
    公共的挂买单的下单方法
    1。下单
    2。写入数据库
    :return:
    '''
    # 挂单
    #time.sleep(1.0)
    place_order_res = place_order(ROOT_URL,API_KEY,SECRET_KEY,symbol,"%.8f" % float(buyprice),
                                  "%.8f" % (float(amount) / float(buyprice)),
                                  'BID', 'LIMIT_ORDER')
    if str(place_order_res['code'])=='200':
        print("订单正常!")
        place_order_id = place_order_res['data']

        print("已挂买单，单号是=》", place_order_id)
        # price = None
        # state = "NEW"
        # ordertype = "BID"
        # 查询订单的状态
        #time.sleep(1.0)
        query_order_res = query_order(ROOT_URL,API_KEY,SECRET_KEY,place_order_id)
        price = query_order_res['data'][0]['price']
        state = query_order_res['data'][0]['state']
        ordertype = query_order_res['data'][0]['type']

        print("挂单价格为", "%.8f" % float(buyprice), "实际生成的价格", price, "状态", state, "类型", ordertype)
        # logstr = "挂单价格为"+("%.8f" % float(buyprice))+"实际生成的价格"+str(price)+ "状态"+ str(state)+ "类型"+ str(ordertype)
        # writelog(logstr)

        # 按照利润点算出该挂出去的卖价
        temp_sell_price = '%.8f' % (float(price)*(1.002/(0.998-float(profit_rate))))
        # temp_sell_price = '%.4f' % ((1.004 + 1.002 * profit_rate) * float(price))
        # 获取当前时间
        temp_sell_price = str(delete_extra_zero(float(temp_sell_price)))
        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        buyprice = str(delete_extra_zero(float(buyprice)))
        # 写入数据库，链接数据库
        sqlstr = "INSERT INTO grid_BidOrder_tb (userkey,order_id,symbol,last_order_id,praper_price,real_price,status,prepare_sell_price,order_type,create_time) VALUES " \
                 "(\"%s\", \"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\", \"%s\", \"%s\")" % (
                     API_KEY, place_order_id, symbol, last_order_id, str(buyprice),price, "NEW", temp_sell_price, ordertype, now_time)

        # logstr = "需要更新买单价格的monitor价格==》" + str(buyprice)
        # writelog(logstr)
        connect_db_excute(db_path, sqlstr)
    else:
        msg = place_order_res['msg']
        print("订单异常，请查看!",msg)


def compare_use_num(ROOT_URL,API_KEY,SECRET_KEY,amount):
    '''
    判断余额跟准备的使用量是否匹配
    :return:
    '''
    # 获取账户的可用量,并进行判断
    get_account_info_res = get_account_info(ROOT_URL,API_KEY,SECRET_KEY)
    avaliable_usdt = get_account_info_res["data"]["USDT"]["available"]
    if(int(float(avaliable_usdt))>=int(float(amount))):
        return float(amount)
    else:
        return float(avaliable_usdt)

def monitor_order(ROOT_URL,API_KEY,SECRET_KEY,symbol,monitor_dic_list,per_usdt,profit_rate,dbpath,cancel_orderlist):
    '''
    监控订单.
    没有就下单，有就监控着
    :return:
    '''
    ##获取当前此刻的价格
    get_ticker_res = get_ticker(ROOT_URL,API_KEY,symbol)
    # get_1m_kline_res = get_kline(symbol, '1m')
    now_time = get_ticker_res['data'][0]["time"]
    now_price = get_ticker_res['data'][0]["last"]
    print("当前的时间是:", CovertTime(now_time), "当前的价格是:", now_price)

    # 先遍历数据库中的单子
    querysqlforbid = "SELECT order_id,praper_price FROM grid_BidOrder_tb where " \
               "userkey=\"%s\" and status=\"NEW\" and symbol=\"%s\" and update_time IS NULL " % (API_KEY, symbol)

    quersqlforask ="SELECT order_id,praper_sell_price FROM grid_AskOrder_tb where " \
               "userkey=\"%s\" and status=\"NEW\" and symbol=\"%s\" and update_time IS NULL " % (API_KEY, symbol)
    scan_orderbid_dic = connect_db_search_all_orders(dbpath, querysqlforbid)
    scan_orderask_dic = connect_db_search_all_orders(dbpath, quersqlforask)
    if (scan_orderbid_dic is None):
        print("未查询到买单=====>")
    else:
        # 遍历 字典查询订单
        for k, v in scan_orderbid_dic.items():
            # time.sleep(3.0)
            temp_query_res = query_order(ROOT_URL,API_KEY,SECRET_KEY,k)
            temp_status = temp_query_res['data'][0]['state']
            order_type = temp_query_res['data'][0]['type']
            if (temp_status == "FILLED"):  # 订单成交,更新数据状态
                amount = temp_query_res['data'][0]['deal_quantity']  # 成交量
                p_price = temp_query_res['data'][0]['price']  # 挂单价格
                # 写入到数据库中
                # 获取当前时间
                temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatesql = "UPDATE grid_BidOrder_tb set update_time " \
                            "= \"%s\",status= \"%s\" where order_id=\"%s\"" % (temp_now_time, temp_status, k)
                connect_db_excute(dbpath, updatesql)
                print("已将订单号为", k, "的订单状态更新为", temp_status)
                # 挂单，如果类型是买单那么就下卖单
                if (order_type == 'BID'):
                    # 挂卖单 v是预期的买价。需要挂预期的卖价
                    # time.sleep(1.0)
                    # tmp_sell_price = '%.4f' % ((1.004 + 1.002 * profit_rate) * float(v))
                    tmp_sell_price = '%.8f' % (float(v)*(1.002/(0.998-float(profit_rate))))


                    sell_order_res = place_order(ROOT_URL,API_KEY,SECRET_KEY,symbol, '%.8f' % float(tmp_sell_price), amount, "ASK",
                                                 "LIMIT_ORDER")
                    # 获取出卖单的 信息插入数据库
                    sell_order_id = sell_order_res['data']
                    time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    # 查询订单的状态
                    # time.sleep(1.0)
                    query_order_res = query_order(ROOT_URL,API_KEY,SECRET_KEY,sell_order_id)
                    price = query_order_res['data'][0]['price']
                    state = query_order_res['data'][0]['state']
                    ordertype = query_order_res['data'][0]['type']

                    # 写入数据库，链接数据库

                    tmp_sell_price= str(delete_extra_zero(float(tmp_sell_price)))
                    sqlstr = "INSERT INTO grid_AskOrder_tb (userkey,symbol,last_order_id,order_id,praper_sell_price," \
                             "real_sell_price,status,order_type,create_time) VALUES " \
                             "(\"%s\", \"%s\",\"%s\", \"%s\", \"%s\",\"%s\",\"%s\",  \"%s\", \"%s\")" % (
                                 API_KEY, symbol, k, sell_order_id, tmp_sell_price, price, "NEW", ordertype, time_now)
                    # logstr = "需要更新卖单价格的monitor价格==》" + str(tmp_sell_price)
                    # writelog(logstr)
                    connect_db_excute(dbpath, sqlstr)
                elif(order_type == 'BID'):
                    print("理论上不存在此中情况，请检查代码!")
            elif (temp_status == "NEW"):
                print("订单号为", k, "的订单状态", temp_status, "继续监控")
            else:  # 直接更新数据状态
                # 获取当前时间
                temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatesql = "UPDATE grid_BidOrder_tb set update_time " \
                            "= \"%s\",status= \"%s\" where order_id=\"%s\"" % (temp_now_time, temp_status, k)
                connect_db_excute(dbpath, updatesql)
                print("已将订单号为", k, "的订单状态更新为", temp_status)

    if (scan_orderask_dic is None):
        print("未查询到卖单=====>")
    else:
        # 遍历 字典查询订单
        for kk, vv in scan_orderask_dic.items():
            # time.sleep(3.0)
            temp_query_res = query_order(ROOT_URL,API_KEY,SECRET_KEY,kk)
            temp_status = temp_query_res['data'][0]['state']
            order_type = temp_query_res['data'][0]['type']
            if (temp_status == "FILLED"):  # 订单成交,更新数据状态
                qulity = temp_query_res['data'][0]['deal_quantity']  # 成交量
                amount = temp_query_res['data'][0]['deal_amount']  # 成交金额
                p_price = temp_query_res['data'][0]['price']  # 挂单价格
                ask_time = temp_query_res['data'][0]['create_time']  # 挂单时间
                # 写入到数据库中
                # 获取当前时间
                temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatesql = "UPDATE grid_AskOrder_tb set update_time " \
                            "= \"%s\",status= \"%s\" where order_id=\"%s\"" % (temp_now_time, temp_status, kk)
                connect_db_excute(dbpath, updatesql)
                print("已将订单号为", kk, "的订单状态更新为", temp_status)
                # 卖单已完成。现将完整数据写入 完整库中。
                #查询出所需要的单子然后写入
                querybidorderid = "SELECT last_order_id from grid_AskOrder_tb where order_id =\"%s\""%(kk)
                result_list = connect_db_search(querybidorderid)
                #查询userid
                queryuseridstr ="select Uniqueid from trade_user_info where ak =\"%s\""%(API_KEY)
                userid_list = connect_db_search(queryuseridstr)
                userkey = userid_list[0]['Uniqueid']
                if len(result_list)>0:
                    bidorderid = result_list[0]['last_order_id']
                    # 查询订单的信息
                    temp_bidquery_res = query_order(ROOT_URL, API_KEY, SECRET_KEY, bidorderid)
                    tempbidprice = temp_bidquery_res['data'][0]['price']
                    tempbidqulity = temp_bidquery_res['data'][0]['deal_quantity']
                    tempbidamount = temp_bidquery_res['data'][0]['deal_amount']
                    bidcreatetime = temp_bidquery_res['data'][0]['create_time']
                    bidcreatetime = CovertTime(bidcreatetime)
                    askoredrID = kk
                    askorderPrice = p_price
                    askorderQulity = qulity
                    askoderamount = amount
                    # askcreatetime = CovertTime(ask_time)  # 订单创建时间
                    askorderdealtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    orderprofit  = "%.6f" % (float(askoderamount) - float(tempbidamount))
                    print("走到这里了！")
                    orderprofitrate = ("%.2f" % (float(orderprofit)/float(tempbidamount)*100))+"%"
                    sqlrc = "INSERT INTO  trade_completeordertb (CoinPair,UserUniqkey,Bidorderid,Bidprice,Bidqulity," \
                            "BidAmount,BidCreateTime,Askorderid,Askprice,Askqulity,AskAmount,AskCreateTime,OrderProfit," \
                            "OrderProfitrate) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\"," \
                            "\"%s\",\"%s\",\"%s\",\"%s\")"%(symbol,userkey,bidorderid,tempbidprice,tempbidqulity,
                            tempbidamount,bidcreatetime,askoredrID,askorderPrice,askorderQulity,askoderamount,askorderdealtime,
                            orderprofit,orderprofitrate)
                    print("z重要插入的数据=============>",sqlrc)
                    connect_db_excute(dbpath, sqlrc)

                else: #未查询到订单1
                    print("对应的卖单未查询到相应的买单")

                # 挂单，如果类型是买单那么就下卖单
                if (order_type == 'BID'):
                    print("理论上代码不会走到这里。代码逻辑存在问题，请检查！")
                elif (order_type == 'ASK'):  # 如果类型是卖单，那么就下买单
                    # 挂买单 重新获取的新的区间
                    amount = compare_use_num(ROOT_URL,API_KEY,SECRET_KEY,amount)
                    print("卖完后的买总量amount",amount)
                    # 根据 last_order_id 查询本卖单是来自于哪一个买单价格的。
                    query_sql="select a.praper_price from grid_BidOrder_tb a LEFT JOIN grid_AskOrder_tb b on " \
                              "a.order_id = b.last_order_id where b.order_id =\"%s\""%(kk)
                    conn = sqlite3.connect(dbpath)
                    c = conn.cursor()
                    # print("Opened database successfully")
                    cursor = c.execute(query_sql)
                    print("挂完买单后挂卖单！",cursor)
                    praperbuyprice = []
                    for row in cursor:
                        praperbuyprice.append(row[0])
                    conn.close()
                    praperprice = praperbuyprice[0]

                    # 挂单
                    common_buy_order(ROOT_URL=ROOT_URL,API_KEY=API_KEY,SECRET_KEY=SECRET_KEY,
                                     symbol=symbol, buyprice="%.8f" % float(praperprice), amount=amount,
                                     profit_rate=profit_rate,db_path=dbpath)

            elif (temp_status == "NEW"):
                print("订单号为", kk, "的订单状态", temp_status, "继续监控")
            else:  # 直接更新数据状态
                # 获取当前时间
                temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatesql = "UPDATE grid_AskOrder_tb set update_time " \
                            "= \"%s\",status= \"%s\" where order_id=\"%s\"" % (temp_now_time, temp_status, kk)
                connect_db_excute(dbpath, updatesql)
                print("已将订单号为", kk, "的订单状态更新为", temp_status)

    #查询BId 表更新 需要监控的 dic的状态
    #遍历monitor dic 更新状态
    for i in range(len(monitor_dic_list)):
        praper_buy_price=monitor_dic_list[i]['praper_buy_price']
        queryorderstr="select praper_price,status from grid_BidOrder_tb where " \
                      "symbol =\"%s\" and userkey=\"%s\" and praper_price =\"%s\" " \
                      "ORDER BY id DESC LIMIT 1"%(symbol,API_KEY,praper_buy_price)
        scan_order_dicy=connect_db_search_all_orders(dbpath,queryorderstr)
        if(scan_order_dicy is None):
            continue
        else:
            if (scan_order_dicy[praper_buy_price]== "NEW" or scan_order_dicy[praper_buy_price] == "PARTIALLY_FILLED"):
                monitor_dic_list[i]['praper_buy_staus'] ="1" # 设置状态是1
            else:
                monitor_dic_list[i]['praper_buy_staus'] ="0" # 设置状态是2

    # # 查询ASK表，更新需要监控的monitordic状态

    for i in range(len(monitor_dic_list)):
        praper_sell_price=monitor_dic_list[i]['praper_sell_price']
        queryaskstr="select praper_sell_price,status from grid_AskOrder_tb where " \
                      "symbol =\"%s\" and userkey=\"%s\" and praper_sell_price =\"%s\" " \
                      "ORDER BY id DESC LIMIT 1"%(symbol,API_KEY,praper_sell_price)
        scan_askorder_dicy=connect_db_search_all_orders(dbpath,queryaskstr)
        if(scan_askorder_dicy is None):
            continue
        else:
            if (scan_askorder_dicy[praper_sell_price]== "NEW" or scan_askorder_dicy[praper_sell_price] == "PARTIALLY_FILLED"):
                monitor_dic_list[i]['praper_sell_staus'] ="1" # 设置状态是1
            else:
                monitor_dic_list[i]['praper_sell_staus'] ="0" # 设置状态是2

    # 检查monitordic 的状态
    print("此时的monitor价格==》",monitor_dic_list)
    # logstr = "此时的monitor状态:====》" + str(monitor_dic_list)
    # writelog(logstr)
    for tep_monitor_dic in monitor_dic_list:
        if(tep_monitor_dic['praper_buy_staus']=='1' and tep_monitor_dic['praper_sell_staus']=='1'):
            print("对应的买单和卖单均有价格，撤销买单")
            buyprice = tep_monitor_dic['praper_buy_price']
            #查询bid表。该价格的订单号
            querstr="select order_id from grid_BidOrder_tb where " \
                    "praper_price=\"%s\" and status=\"NEW\" and update_time is null"%(buyprice)
            print("获取order sql===>",querstr)
            conn = sqlite3.connect(dbpath)
            c = conn.cursor()
            print("Opened database successfully")
            cursor = c.execute(querstr)
            cancelorderlist = []
            for row in cursor:
                cancelorderlist.append(row[0])
            conn.close()
            if(len(cancel_orderlist)>0):
                cancelbuyorderid =cancelorderlist[0]
                cancel_order(ROOT_URL,API_KEY,SECRET_KEY,cancelbuyorderid)
                print("已撤销重复的买单!")
            else:
                print("买单生成的卖单已挂上。")

        elif (tep_monitor_dic['praper_buy_staus']=='1' and tep_monitor_dic['praper_sell_staus']=='0'):
            print("挂单正常！")
        elif (tep_monitor_dic['praper_buy_staus']=='0' and tep_monitor_dic['praper_sell_staus']=='1'):
            print("买单已完成，卖单在售，正常！")
        else:

            #需要挂买单 判断当前价格是否高于列表价格，若是低于，那么列表价格就不需要 挂单

            if(float(now_price)>float(tep_monitor_dic['praper_buy_price'])):
                print(get_account_info(ROOT_URL,API_KEY,SECRET_KEY))
                print("此时需要买的 价格是==》",tep_monitor_dic['praper_buy_price'],"买的量是==》",per_usdt)
                common_buy_order(ROOT_URL=ROOT_URL,API_KEY=API_KEY,SECRET_KEY=SECRET_KEY,symbol=symbol,
                                 buyprice=tep_monitor_dic['praper_buy_price'], amount=per_usdt,
                                 db_path=dbpath,profit_rate=profit_rate)
            else:
                print("当前价格未达到网格价格",tep_monitor_dic['praper_buy_price'],"无需挂单！")



class Mxc_Task:
    def __init__(self,API_KEY,SECRET_KEY,ROOT_URL):
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.ROOT_URL = ROOT_URL

    def starttask(self,symbol,profit_rate,the_highest_price,the_lowest_price,grid_num,Usdtnum):

        search_period = float(10.0)  # 查询周期s
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')


        # 获取到网格价格区间
        per_step = (float(the_highest_price) - float(the_lowest_price)) / grid_num
        print("步长", per_step)

        step_price_list = []  # 存放网格价格的列表
        for i in range(1, grid_num):
            step_price_list.append(float("%.8f" % (float(the_lowest_price) + per_step * i)))

        # 根据step_price_list 可以得到需要监控的买和卖单的列表价
        monitor_dic_list = []
        for tmp_price in step_price_list:
            # tmp_sell_price = '%.4f' % ((1.004 + 1.002 * profit_rate) * float(tmp_price))
            tmp_sell_price = '%.8f' % (float(tmp_price)*(1.002/(0.998-float(profit_rate))))
            tmp_sell_price = delete_extra_zero(float(tmp_sell_price))
            tmp_price = delete_extra_zero(float(tmp_price))
            monitor_dic_list.append({
                "praper_sell_price": str(tmp_sell_price),
                "praper_buy_price": str(tmp_price),
                "praper_buy_staus": "0",
                "praper_sell_staus": "0"
            })
        # logstr = "monitor的初始值为=》"+str(monitor_dic_list)
        # writelog(logstr)
        sort_step_price_list, index, now_price = get_sorted_price_list(self.ROOT_URL,self.API_KEY,step_price_list, symbol)

        # 撤销该币种的所有买单，且更新数据库。重新按照新的策略挂单
        # 查询该币种下所有的单子
        open_orders_res = get_open_orders(self.ROOT_URL,self.API_KEY,self.SECRET_KEY,symbol)
        open_order_list = open_orders_res['data']
        cancel_orderlist = []
        if (len(open_order_list) <= 0):
            print("未挂单，无需撤单!")
            # logstr = "未挂单，无需撤单!"
            # writelog(logstr)
        else:
            for order in open_order_list:
                if (order['type'] == 'BID' and (order['state'] == 'NEW' or order['state'] == 'PARTIALLY_FILLED')):
                    cancel_orderlist.append(order['id'])
            # 撤销订单 切割成长度为20的 list
            f = lambda a: map(lambda b: a[b:b + 20], range(0, len(a), 20))
            for orderid in f(cancel_orderlist):
                cancel_order(self.ROOT_URL,self.API_KEY,self.SECRET_KEY,orderid)
            print("初始化撤销订单完成！")
            # logstr = "初始化撤销订单完成！"
            # writelog(logstr)
        # 更新数据库 查询买和卖的表
        querysql = "SELECT order_id,praper_price FROM grid_BidOrder_tb where " \
                   "userkey=\"%s\" and (status=\"NEW\" or status=\"PARTIALLY_FILLED\") and symbol=\"%s\" and update_time IS NULL " % (
                   self.API_KEY, symbol)
        # scan_order_dic = connect_db_search_all_orders(db_path, querysql)

        querysqlaskl = "SELECT order_id,praper_sell_price FROM grid_AskOrder_tb where " \
                       "userkey=\"%s\" and (status=\"NEW\" or status=\"PARTIALLY_FILLED\") and symbol=\"%s\" and update_time IS NULL " % (
                           self.API_KEY, symbol)
        scan_order_dicbid = connect_db_search_all_orders(db_path, querysql)
        scan_order_dicask = connect_db_search_all_orders(db_path, querysqlaskl)
        if (scan_order_dicbid is None):
            print("未在库里面查询到结果,无需更新！")
            # logstr = "未在库里面查询到结果,无需更新！"
            # writelog(logstr)
        else:
            for k, v in scan_order_dicbid.items():
                # time.sleep(3.0)
                temp_query_res = query_order(self.ROOT_URL,self.API_KEY,self.SECRET_KEY,k)
                temp_status = temp_query_res['data'][0]['state']
                order_type = temp_query_res['data'][0]['type']
                # 全部更新状态
                # 获取当前时间
                temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatesql = "UPDATE grid_BidOrder_tb set status= \"%s\",update_time=\"%s\" " \
                            "where order_type=\"%s\" and order_id=\"%s\"" % (temp_status,temp_now_time,order_type,k)
                connect_db_excute(db_path, updatesql)
                print("已将订单号为", k, "的订单状态更新为", temp_status)
                # logstr = "已将订单号为"+k+"的订单状态更新为"+temp_status
                # writelog(logstr)
        if (scan_order_dicask is None):
            print("未在库里面查询到结果,无需更新！")
        else:
            for kkk, vvv in scan_order_dicask.items():
                # time.sleep(3.0)
                temp_query_res = query_order(self.ROOT_URL,self.API_KEY,self.SECRET_KEY,kkk)
                temp_status = temp_query_res['data'][0]['state']
                order_type = temp_query_res['data'][0]['type']
                # 全部更新状态
                # 获取当前时间
                temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                updatesql = "UPDATE grid_BidOrder_tb set status= \"%s\",update_time=\"%s\" " \
                            "where order_type=\"%s\" and order_id=\"%s\"" % (temp_status, temp_now_time, order_type, kkk)
                connect_db_excute(db_path, updatesql)
                print("已将订单号为", kkk, "的订单状态更新为", temp_status)
                # logstr = "已将订单号为" + kkk + "的订单状态更新为" + temp_status
                # writelog(logstr)
        # 重新挂单
        # 将 可用的 usdt 均分成这些份价格挂单上
        get_account_info_res = get_account_info(self.ROOT_URL,self.API_KEY,self.SECRET_KEY)
        avaliable_usdt = get_account_info_res["data"]["USDT"]["available"]
        print("当前账户USDT", avaliable_usdt, "购买", symbol, "的指定额度是", Usdtnum)
        # logstr = "当前账户USDT"+str(avaliable_usdt)+ "购买"+str(symbol)+"的指定额度是"+str(Usdtnum)
        # writelog(logstr)
        # 判断若avaliable_usdt 若小于 指定的，那么使用当前余额的
        if (float(avaliable_usdt) <= Usdtnum):
            Usdtnum = avaliable_usdt
        # 每份的数量
        per_usdt = float('%.2f' % (float(Usdtnum) / float(grid_num)))
        if (index > 0):  # 证明不是排在第一个也不是最低价
            # 前面也有index 挂单价  例排序后等分价格列表： [0.1534, 0.1856, 0.2177, 0.2499, 0.2821, 0.3143, 0.3465, 当时0.3514, 0.3786, 0.4108]

            # 挂单
            for k in range(1, index + 1):
                temp_price = sort_step_price_list[k - 1]  # 价格
                # 挂单.
                common_buy_order(ROOT_URL=self.ROOT_URL,API_KEY=self.API_KEY,SECRET_KEY=self.SECRET_KEY,symbol=symbol,
                                 buyprice=temp_price, amount=per_usdt,db_path=db_path,profit_rate=profit_rate)

                #首次挂单，挂完买单后需要将 monitor_dic_list 的数据更新
                for i in range(len(monitor_dic_list)):
                    monitor_price = monitor_dic_list[i]['praper_buy_price']
                    if (float(monitor_price) - float(temp_price)) == 0:
                        monitor_dic_list[i]['praper_buy_staus'] = '1'
                # logstr = "已挂了价格为:" + str(temp_price)+"的买单!"
                # writelog(logstr)
        else:  # 证明在第一个
            # 比较当前价格跟 最低价格。谁最低就挂谁
            print('网格区间设置存在问题。请重新设置!')
        # logstr = "初始挂完单后monitor状态:"+ str(monitor_dic_list)
        # writelog(logstr)
        while (True):
            try:
                monitor_order(self.ROOT_URL,self.API_KEY,self.SECRET_KEY,symbol,monitor_dic_list,
                              per_usdt, profit_rate, db_path,cancel_orderlist)
            except Exception as e:
                print("有异常", e)
            time.sleep(search_period)




