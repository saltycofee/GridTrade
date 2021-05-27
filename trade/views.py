from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view,permission_classes
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from trade.CommonTools import CommonTool,get_account_info
from rest_framework.response import Response
import sqlite3
import xml.etree.ElementTree as ET
import queue
from trade.models import User_info,Task_info,CompleteOrdertb,TaskRuninfo,TradePlant
import logging
import hashlib,time,datetime
import json
import os
import trade.utils as ut
import threading
# 引入重要的文件 主要的执行任务
from trade import mxc_task


# @csrf_exempt
# @api_view(http_method_names=['get','post'])
# @permission_classes((permissions.AllowAny,))
# def testdata(request):
#
#     postbody = request.body.decode()
#     bodydata = json.loads(postbody)
#     data = bodydata['data']
#     te =ut.testpool()
#     t =threading.Thread(target=te.testrunthread, args=(data,))
#     t.start()
#     ut.poolstatuslist[data]= t
#     # futrue = ut.thread_pools.submit(te.testrunthread,data)
#     # ut.poolstatuslist[futrue] = data
#     return Response({"code": "0000", "message": "添加成功！", "data": []})
#
#
# @csrf_exempt
# @api_view(http_method_names=['get','post'])
# @permission_classes((permissions.AllowAny,))
# def crashthread(request):
#
#     postbody = request.body.decode()
#     bodydata = json.loads(postbody)
#     data = bodydata['data']
#     child_thread = ut.poolstatuslist[data]
#     print("即将终止的线程===>",child_thread)
#     print(child_thread.ident)
#     #终止线程
#     ut._async_raise(child_thread.ident, SystemExit)
#     # futrue = ut.thread_pools.submit(te.testrunthread,data)
#     # ut.poolstatuslist[futrue] = data
#     return Response({"code": "0000", "message": "终止线程成功！", "data": []})



@csrf_exempt
@api_view(http_method_names=['get','post'])
@permission_classes((permissions.AllowAny,))
def wx_entrance(request):
    '''获取传入的参数'''
    if request.method == 'GET':
        signature = request.GET.get('signature')
        echostr = request.GET.get('echostr')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        print(signature, echostr, timestamp, nonce)
        # 微信的token
        token = 'WXCoin'
        listing = [token, timestamp, nonce]
        listing.sort()
        # 生成新的字符串
        listing2 = ''.join(listing)
        sha1 = hashlib.sha1()
        sha1.update(listing2.encode('utf-8'))
        hashcode = sha1.hexdigest()
        if hashcode == signature:
            return HttpResponse(echostr)
    elif request.method == 'POST':
        postbody =request.body
        #print(postbody)
        rootbody =ET.fromstring(postbody)
        #print(rootbody)
        #获取发送消息的微信号
        fromUser = rootbody.findtext('.//FromUserName')
        #print(fromUser)
        toUser = rootbody.findtext('.//ToUserName')
        CreateTime = rootbody.findtext('.//CreateTime')
        MsgType = rootbody.findtext('.//MsgType')
        Event = rootbody.findtext('.//Event')
        Content = rootbody.findtext('.//Content')
        mix_res = CommonTool()
        # 这里写分支，设置价格提醒。
        if Content =='绑定模版':
            ReContent = '请按照如下模板设置:' \
                        '账号绑定-API_KEY:xxxxxxxxxxxxx,' \
                        'SECRET_KEY:xxxxxxxxxx,' \
                        '交易所:抹茶'
        elif '账号绑定' in Content:
            ReContent = mix_res.BindKey(Content, fromUser)
        else:
            ReContent = Content

        res = mix_res.mix_response_message(fromUser, toUser, CreateTime, MsgType, ReContent)
        return HttpResponse(res)


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def create_task(request):
    ''''
    创建网格策略任务
    '''
    postbody = request.body.decode()
    ctool = CommonTool()
    # print(postbody)

    bodydata = json.loads(postbody)
    uid=bodydata['uid']

    # 校验消息的uid
    if ctool.checkUid(uid)==False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})

    '''dics = {"uid":"12344","data":{"taskname":"","plant":"","symbol":"","highestprice":"","lowestprice":"","locknum":"","gridnum":"","siglerate":""}
    '''
    data = bodydata['data']
    taskname = data['taskName'] #任务名称
    plant = data['PlantName'] #交易所名称
    symbol = data['Symbol'] #交易对
    highestprice = data['HighPrice'] #最高价
    lowestprice = data['LowPrice']  #最低价
    locknum = data['Locknum']  #准备分配的Usdt 数量
    gridnum = data['GridNum']  #网格数量
    siglerate = data['ProfitRate']  #每单套利数量

    #校验任务是否重复
    if ctool.checkTask(uid,taskname,plant,symbol)==False:
        return Response({"code": "9999", "message": "任务重复，建议一个货币对对应一个任务.", "data": []})
    #校验锁定的USDT与可用的USDT数量

    if ctool.checklocknum(uid,locknum,plant)==False:
        # return HttpResponse("锁仓数量大于可用数量，请重新配置")
        return Response({"code": "9999", "message": "锁仓数量大于可用数量，请重新配置", "data": []})


    # 校验 每笔单子的数量是否超过5USDT
    if (float(locknum)/float(gridnum)) <5.0:
        # return HttpResponse("每单的数量不得小于5usdt")
        return Response({"code": "9999", "message": "每单的数量不得小于5usdt", "data": []})

    #校验通过后写入库里
    try:
        Task_info.objects.create(Uniqueid=uid, TaskName=taskname, TradePlantName=plant
                                 , CoinExchange=symbol,HighestPrice=str(highestprice)
                                 ,lowestPrice=str(lowestprice),lockNum=str(locknum),
                                 gridnum=str(gridnum),trate=str(siglerate),
                                 task_flag="1")

    except Exception as e:
        print(e)
        # return  HttpResponse("数据库执行错误，请检查")
        return Response({"code": "9999", "message": "数据库执行错误，请检查.", "data": []})

    # return HttpResponse("网格任务创建成功！")
    #查询任务的id
    return Response({"code": "0000", "message": "网格任务创建成功！", "data": []})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def search_account(request):
    ''''
    查询账户信息
    '''
    postbody = request.body

    bodydata = json.loads(postbody)
    uid=bodydata['uid']
    # 校验消息的uid
    ctool = CommonTool()
    if ctool.checkUid(uid) == False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})
    uplant = bodydata['plant']
    item = User_info.objects.filter(Uniqueid=uid, tradeplant=uplant)[0]
    ak = item.ak
    sk = item.sk
    hostapi = TradePlant.objects.filter(plantName=uplant)[0].plantApiHost
    try:
        get_account_info_res = get_account_info(hostapi, ak, sk)
    except Exception as e:
        print("用户信息获取有误", e)
        return Response({"code": "9999", "message": "用户信息获取有误,请重新尝试", "data": []})
    return Response({'code': '0000', 'message': '请求成功。', 'data': get_account_info_res})

@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def get_taskinfo(request):
    '''
    查询该账户下的任务列表
    :param request:
    :return:
    '''
    postbody = request.body.decode()
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})

    #查询用户的任务列表
    tasklist = Task_info.objects.filter(Uniqueid=uid,task_flag='1')
    usertaskinfolist =[]
    if tasklist:
        for item in tasklist:
            create_date = item.create_date.strftime('%Y-%m-%d %H:%M:%S')
            # print(create_date)
            taskname = item.TaskName
            plantname = item.TradePlantName
            symbol = item.CoinExchange
            highprice = item.HighestPrice
            lowprice = item.lowestPrice
            gridnum = item.gridnum
            taskid = item.Tid
            # 查询该任务的运行状态
            # print(uid,taskid,taskname)
            runtask = TaskRuninfo.objects.filter(Uniqueid=uid, taskid=taskid, TaskName=taskname)
            if runtask:
                taskstatus = runtask[0].flag
            else:
                taskstatus ="0"
            # print(taskstatus)
            # return ""
            usertaskinfolist.append({'id':taskid,'create_date':create_date,
                                     'taskname':taskname,'plantname':plantname,
                                     'symbol':symbol,'highprice':highprice,'lowprice':lowprice,
                                     'gridnum':gridnum,'taskstatus':taskstatus})
        return Response({'code':'0000','message':'请求成功!','data':usertaskinfolist})
    else:
        return Response({'code': '0000', 'message': '请求成功!', 'data': usertaskinfolist})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def delete_task(request):
    '''
    删除任务
    :param request:
    :return:
    '''
    postbody = request.body
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})
    #获取需要删除的任务id
    taskid = bodydata['taskid']
    try:
        task=Task_info.objects.filter(Uniqueid=uid,Tid=taskid)[0]
        task.task_flag ='0'
        task.save()
        return Response({'code': '0000', 'message': '请求成功。',"data": []})
    except Exception as e:
        print(e)
        return Response({'code': '9999', 'message': '处理异常。',"data": []})




@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def start_task(request):
    '''
    开启任务
    :param request:
    :return:
    '''
    pass


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def stop_task(request):
    '''
    结束任务
    :param request:
    :return:
    '''
    pass


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def getkey_info(request):
    '''
    获取APIkey
    :param rquest:
    :return:
    '''
    postbody = request.body
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code":"5555","message":"用户不存在，非法请求","data":[]})

    uplant = '抹茶'  # 只有一个，目前
    try:
        item = User_info.objects.filter(Uniqueid=uid, tradeplant=uplant)[0]
        ak = item.ak
        sk = item.sk
        return Response({'code': '0000', 'message': '请求成功!', 'data': [{'ak':ak,'sk':sk}]})
    except Exception as e:
        print(e)
        return Response({"code": "9999", "message": "用户apikey信息获取失败。", "data": []})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def get_profitinfo(request):
    '''
    获取收益信息
    :param request:
    :return:
    '''
    postbody = request.body
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code":"5555","message":"用户不存在，非法请求","data":[]})

    #获取用户的uid.以及查询的时间
    start_date = bodydata['start_date']
    end_date = bodydata['end_date']
    # 查询收益表中的数据
    querysql = "select Bidprice,Bidqulity,BidAmount,BidCreateTime,Askprice,AskAmount,CoinPair,AskCreateTime,Askqulity,OrderProfit,OrderProfitrate from trade_completeordertb " \
               "where UserUniqkey=\"%s\" and SUBSTR(AskCreateTime,0,11) BETWEEN \"%s\" AND \"%s\""%(uid,start_date,end_date)

    result_list =ctool.connect_db_search_all_orders(querysql)
    return Response({'code': '0000', 'message': '请求成功!', 'data': result_list})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def get_orderrecord(request):
    '''
    获取按天纬度统计的做单记录.按照一周的时间来统计
    :param request:
    :return:
    '''
    postbody = request.body
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code":"5555","message":"用户不存在，非法请求","data":[]})
    # 计算一周的日期列表
    weeklist =ctool.get_week_list()
    querysql = "select SUBSTR(AskCreateTime,0,11) as date,count(1) as num from " \
               "trade_completeordertb where UserUniqkey=" + uid + " and " \
                                                                  "SUBSTR(AskCreateTime,0,11) in " + str(
        tuple(weeklist)) + " GROUP BY SUBSTR(AskCreateTime,0,11)"
    # print(querysql)

    result_list = ctool.connect_db_search_all_orders(querysql)
    # print(result_list)
    return Response({"code":"0000","message":"请求成功","data":result_list})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def get_profitrecord(request):
    '''
    获取按天纬度统计的利润记录图
    :param request:
    :return:
    '''
    postbody = request.body
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code":"5555","message":"用户不存在，非法请求","data":[]})
    # 计算一周的日期列表
    weeklist = ctool.get_week_list()
    querysql = "select SUBSTR(AskCreateTime,0,11) as date,sum(OrderProfit) as profi from " \
               "trade_completeordertb where UserUniqkey=" + uid + " and " \
                                                                  "SUBSTR(AskCreateTime,0,11) in " + str(
        tuple(weeklist)) + " GROUP BY SUBSTR(AskCreateTime,0,11)"
    # print(querysql)

    result_list = ctool.connect_db_search_all_orders(querysql)
    # print(result_list)
    return Response({"code":"0000","message":"请求成功","data":result_list})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def login(request):
    '''
    登录校验
    :param request:
    :return:
    '''
    postbody = request.body
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    if ctool.checkUid(uid) == False:
        return Response({"code":"9999","message":"登录失败","data":[]})
    else:
        return Response({"code": "0000", "message": "登录成功!", "data": []})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def getaccountinfo(request):
    '''
    用户账户信息
    :param request:
    :return:
    '''
    postbody = request.body.decode()
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    plant =bodydata['plant']
    if ctool.checkUid(uid) == False:
        return Response({"code":"5555","message":"用户不存在，非法请求","data":[]})
    #调接口查询账户信息
    plant ="抹茶" #只有这一个
    if ctool.getuserinfo(uid,plant) is False:
        return Response({"code": "9999", "message": "请求失败!", "data": []})
    res_data = ctool.getuserinfo(uid,plant)
    # print(res_data)
    return Response({"code":"0000","message":"请求成功!","data":str(res_data)})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def ContorlTask(request):
    '''
    开始或是停止任务
    :param request:
    :return:
    '''
    postbody = request.body.decode()
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    plant = bodydata['plant']
    excuteowrd = bodydata['excuteword']
    gridnum =bodydata['gridnum']
    highprice = str(bodydata['highprice'])
    lowprice = str(bodydata['lowprice'])
    symbol = bodydata['symbol']
    taskname = bodydata['taskname']

    if ctool.checkUid(uid) == False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})
    # 开始执行脚本 实例化
    # 查询获取 apikey secreatkey rooturl
    userinfoobj = User_info.objects.get(Uniqueid=uid, tradeplant=plant)
    ak = userinfoobj.ak
    sk = userinfoobj.sk
    rooturl = TradePlant.objects.get(plantName=plant).plantApiHost
    # 获取profit 根据价格，任务名称，币种，状态查询。
    taskinfoobj = Task_info.objects.get(Uniqueid=uid, TaskName=taskname, TradePlantName=plant,
                                        CoinExchange=symbol, HighestPrice=highprice, lowestPrice=lowprice,
                                        gridnum=gridnum, task_flag='1')
    profit = taskinfoobj.trate
    locknum = taskinfoobj.lockNum

    taskId = taskinfoobj.Tid
    # 开启另外线程执行任务脚本
    if excuteowrd=='开始':
        mxctask = mxc_task.Mxc_Task(API_KEY=ak,SECRET_KEY=sk,ROOT_URL=rooturl)

        # 执行任务，需要开启新的线程
        # mxctask.starttask(symbol=symbol,profit_rate=profit,the_highest_price=highprice,
        #                   the_lowest_price=lowprice,grid_num=gridnum,Usdtnum=locknum)
        try:
            t = threading.Thread(target=mxctask.starttask, args=(symbol,float(profit),float(highprice),float(lowprice),int(gridnum),float(locknum),))
            t.start()
        except Exception as e:
            print(e)
            return Response({"code": "9999", "message": "任务启动失败！", "data": str(e)})
        # 检查监控的任务表里面有没有写入
        taskruninfoobject=TaskRuninfo.objects.filter(Uniqueid=uid,taskid=taskId,TaskName=taskname)
        if len(taskruninfoobject) <1:
            # 为空，插入数据 获取当前系统时间
            temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sqlstr ="INSERT INTO trade_taskruninfo (Uniqueid,TaskName,taskid,flag,taskstarttime) " \
                    "VALUES(\"%s\",\"%s\",\"%s\",\"1\",\"%s\")"%(uid,taskname,taskId,temp_now_time)
            mxc_task.connect_db_excute(path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
                                       ,sqlstr=sqlstr)
        else: #证明存在，修改状态
            temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updatesql = "UPDATE trade_taskruninfo set flag=\"1\", " \
                        "taskstarttime = \"%s\" where Uniqueid=\"%s\" and TaskName=\"%s\" and taskid=\"%s\""%(temp_now_time,uid
                                                                                             ,taskname,taskId)
            mxc_task.connect_db_excute(
                path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
                , sqlstr=updatesql)

        # 用taskid 与 userid 拼接成data
        data =uid+'-'+str(taskId)
        ut.poolstatuslist[data] = t
        return Response({"code": "0000", "message": "任务启动成功！稍后刷新页面查询状态", "data": []})
    elif excuteowrd=='停止':
        data = uid + '-' + str(taskId)
        # 判断 列表里面是否存在
        if data not in ut.poolstatuslist.keys():
            #证明运行的线程没有这个 任务，应该将任务状态停止
            temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updatesql = "UPDATE trade_taskruninfo set flag=\"0\", " \
                        "taskstoptime = \"%s\" where Uniqueid=\"%s\" and TaskName=\"%s\" and taskid=\"%s\"" % (
                            temp_now_time, uid
                            , taskname, taskId)
            mxc_task.connect_db_excute(
                path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
                , sqlstr=updatesql)
            return Response({"code": "9999", "message": "存在错误，但已更正！", "data": []})
        else:
            child_thread = ut.poolstatuslist[data]

        print("即将终止的线程===>", child_thread)
        print(child_thread.ident)
        try:
            # 终止线程
            ut._async_raise(child_thread.ident, SystemExit)
        except Exception as e:

            return Response({"code": "9999", "message": "终止线程失败！", "data": str(e)})

        # 更新数据库状态
        taskruninfoobject = TaskRuninfo.objects.filter(Uniqueid=uid, taskid=taskId, TaskName=taskname)
        if len(taskruninfoobject) <1:
            # 为空，插入数据 获取当前系统时间
            return Response({"code": "9999", "message": "程序异常，终止的列表中没数据！", "data": []})
        else:  # 证明存在，修改状态
            temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            updatesql = "UPDATE trade_taskruninfo set flag=\"0\", " \
                        "taskstoptime = \"%s\" where Uniqueid=\"%s\" and TaskName=\"%s\" and taskid=\"%s\"" % (
                        temp_now_time, uid
                        , taskname, taskId)
            mxc_task.connect_db_excute(
                path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
                , sqlstr=updatesql)
            time.sleep(0.3)
        return Response({"code": "0000", "message": "终止任务成功,刷新查看！", "data": []})
    elif excuteowrd == '移除':
        # 移除任务 修改状态
        temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updatesql = "UPDATE trade_task_info set task_flag=\"0\", updatedate=\"%s\" where Uniqueid=\"%s\" and Tid=\"%s\""%(temp_now_time,uid,str(taskId))
        mxc_task.connect_db_excute(
            path=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3')
            , sqlstr=updatesql)
        return Response({"code": "0000", "message": "任务移除！", "data": []})
    else:
        return Response({"code": "9999", "message": "任务开始停止场景存在错误，请检查！", "data": []})


@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def getorderlist(request):
    '''
    按日期查询订单的数量
    :param request:
    :return:
    '''
    postbody = request.body.decode()
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']
    search_period = bodydata['period']
    start_time = bodydata['start_time']
    end_time = bodydata['end_time']
    if ctool.checkUid(uid) == False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})
    reslut_list=[]
    if search_period =="今天":
        today_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S').split(" ")[0]
        querystr ="select CoinPair as symbol,SUBSTR(AskCreateTime,0,11) as time,Askqulity as num,OrderProfit as profit,OrderProfitrate as profitrate from trade_completeordertb " \
                  "where UserUniqkey=\"%s\" and SUBSTR(AskCreateTime,0,11) = \"%s\""%(uid,today_date)
        reslut_list = ctool.connect_db_search_all_orders(querystr)
    elif search_period =="昨天":
        # 后推120天 就是 + timedelta(days=120)
        daylist = []
        today = datetime.datetime.today()
        today = str(today).split(" ")[0]
        theDay = datetime.datetime.strptime(today, "%Y-%m-%d").date()
        for num in range(1, 2):
            target = theDay - datetime.timedelta(days=num)
            daylist.append(str(target)[:])
        dayalist = daylist[::-1]
        lastday = dayalist[0]
        querystr = "select CoinPair as symbol,SUBSTR(AskCreateTime,0,11) as time,Askqulity as num,OrderProfit as profit,OrderProfitrate as profitrate from trade_completeordertb " \
                   "where UserUniqkey=\"%s\" and SUBSTR(AskCreateTime,0,11) = \"%s\"" % (uid,lastday)
        reslut_list = ctool.connect_db_search_all_orders(querystr)

    elif search_period =="本周":
        # 计算一周的日期列表
        weeklist = ctool.get_week_list()
        querysqlstr ="select CoinPair as symbol,SUBSTR(AskCreateTime,0,11) as time,Askqulity as num," \
                     "OrderProfit as profit,OrderProfitrate as profitrate from " \
                     "trade_completeordertb where UserUniqkey="+uid+ " and  SUBSTR(AskCreateTime,0,11) in " +str(tuple(weeklist))
        print(querysqlstr)
        reslut_list = ctool.connect_db_search_all_orders(querysqlstr)

    elif search_period =="本月":
        # 计算一周的日期列表
        daylist = []
        today = datetime.datetime.today()
        today = str(today).split(" ")[0]
        theDay = datetime.datetime.strptime(today, "%Y-%m-%d").date()
        for num in range(0, 30):
            target = theDay - datetime.timedelta(days=num)
            daylist.append(str(target)[:])
        # dayalist = daylist[::-1]
        querysql = "select CoinPair as symbol,SUBSTR(AskCreateTime,0,11) as time,Askqulity as num," \
                     "OrderProfit as profit,OrderProfitrate as profitrate from " \
                     "trade_completeordertb where UserUniqkey="+uid+ " and  SUBSTR(AskCreateTime,0,11) in " +str(tuple(daylist))
        reslut_list = ctool.connect_db_search_all_orders(querysql)
    elif search_period =="按所选日期查询":
        daylist = ctool.getBetweenDay(start_time,end_time)
        querysql = "select CoinPair as symbol,SUBSTR(AskCreateTime,0,11) as time,Askqulity as num," \
                     "OrderProfit as profit,OrderProfitrate as profitrate from " \
                     "trade_completeordertb where UserUniqkey="+uid+ " and  SUBSTR(AskCreateTime,0,11) in " +str(tuple(daylist))
        reslut_list = ctool.connect_db_search_all_orders(querysql)
    else:
        return Response({"code": "5555", "message": "日期错误！", "data": []})
    #遍历时间list 添加usdt
    if len(reslut_list)<1:
        return Response({"code": "0000", "message": "查询成功!", "data": []})

    returnlist = []
    for li in reslut_list:
        li["coin"] = "USDT"

        returnlist.append(li)
    return Response({"code": "0000", "message": "查询成功!", "data": returnlist})



@csrf_exempt
@api_view(http_method_names=['post'])
@permission_classes((permissions.AllowAny,))
def queryRecord(request):
    '''
    查询收益记录
    :param request:
    :return:
    '''
    postbody = request.body.decode()
    bodydata = json.loads(postbody)
    ctool = CommonTool()
    uid = bodydata['uid']

    if ctool.checkUid(uid) == False:
        return Response({"code": "5555", "message": "用户不存在，非法请求", "data": []})

    # 查询出 每一天的结果与收益
    # 获取出一个月的日期列表
    daylist = []
    today = datetime.datetime.today()
    today = str(today).split(" ")[0]
    theDay = datetime.datetime.strptime(today, "%Y-%m-%d").date()
    for num in range(0, 30):
        target = theDay - datetime.timedelta(days=num)
        daylist.append(str(target)[:])
    dayalist = daylist[::-1]
    querysql = "select SUBSTR(AskCreateTime,0,11) as date,count(1) as num from " \
               "trade_completeordertb where UserUniqkey=" + uid + " and " \
                                                                  "SUBSTR(AskCreateTime,0,11) in " + str(
        tuple(dayalist)) + " GROUP BY SUBSTR(AskCreateTime,0,11)"
    print(querysql)

    result_list = ctool.connect_db_search_all_orders(querysql)
    barxdata =[]
    barydata = []
    if len(result_list)<1:
        for i in dayalist:
            barxdata.append(i[5:])
            barydata.append(0)
    else:
        # datelist =[]
        dic ={}
        for dicc in result_list:
            dic[dicc['date']] = dicc['num']
        for date in dayalist:
            if date in dic.keys():
                barxdata.append(date[5:])
                barydata.append(dic[date])
            else:
                barxdata.append(date[5:])
                barydata.append(0)

    # 汇总利润
    queryprofitstr ="select SUBSTR(AskCreateTime,0,11) as date,SUM(OrderProfit) as profit from " \
           "trade_completeordertb where UserUniqkey="+uid+" and " \
            "SUBSTR(AskCreateTime,0,11) in "+str(tuple(dayalist))+" GROUP BY SUBSTR(AskCreateTime,0,11)"

    profit_result_list = ctool.connect_db_search_all_orders(queryprofitstr)
    linexdata = []
    lineydata = []
    if len(profit_result_list)<1:
        for i in dayalist:
            linexdata.append(i[5:])
            lineydata.append(0)
    else:
        # datelist =[]
        dic ={}
        for dicc in profit_result_list:
            dic[dicc['date']] = dicc['profit']
        for date in dayalist:
            if date in dic.keys():
                linexdata.append(date[5:])
                lineydata.append(dic[date])
            else:
                linexdata.append(date[5:])
                lineydata.append(0)

    result_dic = {
        'barxdata':barxdata,
        'barydata':barydata,
        'linexdata':linexdata,
        'lineydata':lineydata
    }
    return Response({"code": "0000", "message": "请求成功!", "data": [result_dic]})






































