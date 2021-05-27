import requests
import time
import re
import random
import sqlite3
import hmac
import os
from datetime import datetime,timedelta
import hashlib
from trade.models import User_info,Task_info,CompleteOrdertb,TaskRuninfo,TradePlant


def _get_server_time():
    return int(time.time())


def _sign(method, path,API_KEY,SECRET_KEY,original_params=None):
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

def get_account_info(ROOT_URL,API_KEY,SECRET_KEY):
    """account information
        获取账户信息"""
    method = 'GET'
    path = '/open/api/v2/account/info'
    url = '{}{}'.format(ROOT_URL, path)
    params = _sign(method, path,API_KEY,SECRET_KEY)
    response = requests.request(method, url, params=params)
    #print(response.json())
    return response.json()

class CommonTool:
    '''公共方法类'''
    def __init__(self):
        pass

    # 输入毫秒级的时间，转出正常格式的时间
    def timeStamp(self,timeNum):
        timeStamp = float(timeNum / 1000)
        timeArray = time.localtime(timeStamp)
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    def mix_response_message(self, fromUser, toUser, CreateTime, MsgType, Content):
        response_str = '''<xml>
                        <ToUserName><![CDATA['''+fromUser+''']]></ToUserName>
                        <FromUserName><![CDATA['''+toUser + ''']]></FromUserName>
                        <CreateTime>'''+CreateTime+'''</CreateTime>
                        <MsgType><![CDATA['''+MsgType + ''']]></MsgType>
                        <Content><![CDATA['''+Content + ''']]></Content>
                        </xml>'''
        return response_str

    def http_Getmethod(self, url, header):
        '''Get方法'''
        response =requests.get(url=url, headers=header)
        return response.text

    def http_Postmethod(self, url, param, header):
        '''Post方法'''
        #param是字典。判断header里面ContentType是哪种方式
        if header['Content-Type'] == 'application/json':
            return requests.post(url=url, data=param, headers=header).text
        elif header['Content-Type'] == 'application/x-www-form-urlencoded':
            data =''
            for k, v in param.items():
                data = data + k+'='+str(v)+'&'
            data =data[0:-1].encode('utf-8')
            return requests.post(url=url, data=data, headers=header).text

    def recogizetelephone(self,phone):
        '''判断是不是正确的手机号'''
        if len(phone) == 11:
            rp = re.compile('^0\d{2,3}\d{7,8}$|^1[358]\d{9}$|^147\d{8}')
            phoneMatch = rp.match(phone)
            if phoneMatch:  ##判断成功
                return True
            else:
                return False
        else:
            return False

    def connect_db_excute(self, sqlstr,path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')):
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

    # 对apiky,scraetkey进行绑定
    def BindKey(self,Content,fromUser):
        '''
        绑定key
        :param Content:
        :param fromUser:
        :return:
        '''

        '请按照如下模板设置:' \
        '账号绑定-API_KEY:xxxxxxxxxxxxx,' \
        'SECRET_KEY:xxxxxxxxxx,' \
        '交易所:抹茶'
        contentlist = Content.split('-')[1].split(',')
        APKEY = contentlist[0].split(':')[1]
        SCKEY = contentlist[1].split(':')[1]
        TradePlant = contentlist[2].split(':')[1]

        # 随机生成一个uuid
        uid =str(random.randint(100000,999999))
        # 查询是否唯一
        if len(User_info.objects.filter(Uniqueid=uid))<1:
            # 不重复，将数据插入
            try:
                User_info.objects.create(Uniqueid=uid, ak=APKEY, sk=SCKEY
                                                  ,tradeplant=TradePlant)
                return uid
            except Exception as e:
                print(e)
        else:
            #uid 存在，需要重新生成
            return "请重新发送。谢谢～"


    #判断uid是否存在
    def checkUid(self,uid):
        '''
        判断uid是否存在
        :param Uid:
        :return:
        '''
        if len(User_info.objects.filter(Uniqueid=uid)) < 1:
            return False
        else:
            return True

    # 判断任务是否存在
    def checkTask(self,uid,taskname,plant,symbol):
        if len(Task_info.objects.filter(Uniqueid=uid,TaskName=taskname,TradePlantName=plant,CoinExchange=symbol,task_flag="1"))<1:
            return True
        else:
            return False


    #获取用户的信息
    def getuserinfo(self,uid,plant):
        # 根据uid 获取 APIkey，secreatkey , hostapi，
        item = User_info.objects.filter(Uniqueid=uid, tradeplant=plant)[0]
        ak = item.ak
        sk = item.sk
        hostapi = TradePlant.objects.filter(plantName=plant)[0].plantApiHost
        try:
            get_account_info_res = get_account_info(hostapi, ak, sk)
            return get_account_info_res
        except Exception as e:
            print("用户信息获取有误", e)
            return False
    # 判断可用的USDT与准备锁仓的USDT的数量大小
    def checklocknum(self,uid,locknum,plant):
        '''
        检验锁仓数量和可用数量的比
        :param uid:
        :param locknum:
        :return:
        '''
        #根据uid 获取 APIkey，secreatkey , hostapi，
        item = User_info.objects.filter(Uniqueid=uid,tradeplant=plant)[0]
        ak = item.ak
        sk = item.sk
        hostapi = TradePlant.objects.filter(plantName=plant)[0].plantApiHost
        try:
            get_account_info_res = get_account_info(hostapi,ak,sk)
            available_usdt = float(get_account_info_res['data']['USDT']['available'])
        except Exception as e:
            print("用户信息获取有误",e)
            return False
        if float(locknum)<available_usdt:
            return True
        else:
            return False


    # 查询并返回sql的数据
    def connect_db_search_all_orders(self,querysql,path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')):
        '''
        以list的形式返回需要的值
        :param path:
        :return:
        '''
        conn = sqlite3.connect(path)
        c = conn.cursor()
        #print("数据库链接成功")
        #print(querysql)
        cursor = c.execute(querysql)
        list = []
        columns_tuple = cursor.description
        columns_list = [field_tuple[0] for field_tuple in columns_tuple]
        all = cursor.fetchall()  # 获取所有的值
        conn.close()
        for row in all:
            #print(row)
            tempdic = {}
            for i in range(len(columns_list)):
                tempdic[columns_list[i]] = row[i]
            list.append(tempdic)
        return list


    #查询今天往前推一周的时间列表
    def get_week_list(self):
        '''
        查询往前推一周的时间列表
        :return:
        '''
        today = datetime.today()
        today = str(today).split(" ")[0]
        print(today)
        # thatDay = "2020-9-18"
        theDay = datetime.strptime(today, "%Y-%m-%d").date()
        daylist = []
        for num in range(0, 7):
            target = theDay - timedelta(days=num)
            daylist.append(str(target)[-5:])
        # print(daylist[::-1])
        return daylist[::-1]
    #获取两个日期的间隔日期
    def getBetweenDay(self,begin_date, end_date):
        date_list = []
        begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        while begin_date <= end_date:
            date_str = begin_date.strftime("%Y-%m-%d")
            date_list.append(date_str)
            begin_date += timedelta(days=1)
        return date_list

























