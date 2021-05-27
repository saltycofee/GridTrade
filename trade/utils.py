from concurrent.futures import ThreadPoolExecutor,as_completed
import time
import ctypes
import inspect
import os
from trade.CommonTools import CommonTool
import asyncio
import datetime

datalist=[]
poolstatuslist ={}

# def testpool():
#     while True:
#         print("列表数据===>",datalist)
#         time.sleep(5)

class testpool:
    def __init__(self):
        pass
    def testrunthread(self,projectid):
        '''
        这个是一个task任务
        :param projectid:
        :return:
        '''
        flag =True
        num =0
        while flag:
            print(projectid,"num的值===>",num)
            num=num+1
            time.sleep(5)
            if num>18:
                flag =False
        print(projectid,"该函数执行完成")


def checktreadpool():
    '''
    监控线程池
    :return:
    '''
    # obj = thread_pools.submit(testrunthread, page)
    while True:
        #print(poolstatuslist)
        if poolstatuslist:
            #time.sleep()
            # print('进入循环')
            for data in list(poolstatuslist.keys()):
                #print(data,poolstatuslist[data])
                if poolstatuslist[data].isAlive():
                    # 检查数据库的状态更新
                    #print("poolstatuslist[data]线程存活!",data)
                    uid = data.split("-")[0]
                    tid = data.split("-")[1]
                    sqlstr ="SELECT flag from trade_taskruninfo where Uniqueid=\"%s\" and taskid=\"%s\""%(uid,tid)
                    ctool = CommonTool()
                    flag =ctool.connect_db_search_all_orders(sqlstr)[0]['flag']
                    if flag=='1':
                        pass
                else:
                    # 线程停掉了，把状态改了。
                    # 查询 该任务的状态
                    # 检查数据库的状态更新
                    print("poolstatuslist[data]线程死亡!", data)
                    uid = data.split("-")[0]
                    tid = data.split("-")[1]
                    sqlstr = "SELECT flag from trade_taskruninfo where Uniqueid=\"%s\" and taskid=\"%s\"" % (uid, tid)
                    ctool = CommonTool()
                    flag = ctool.connect_db_search_all_orders(sqlstr)[0]['flag']
                    if flag=='1':
                        temp_now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        updatestr = "UPDATE trade_taskruninfo set flag=\"0\", taskstoptime = \"%s\" where " \
                                    "Uniqueid=\"%s\" and taskid=\"%s\"" % (temp_now_time, uid, tid)
                        ctool.connect_db_excute(updatestr)
                    else:
                        pass
                    poolstatuslist.pop(data) # 移除线程池

        else:
            print("没有任务执行!")
            time.sleep(5)


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    try:
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            # pass
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")
    except Exception as err:
        print(err)


def writelog(log):
    '''
    记录日志
    :return:
    '''
    fpath = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'logs'),'log.log')
    with open(file = fpath,mode='a',encoding='utf-8') as f:
        f.write(log+'\n')
    f.close()

def delete_extra_zero(n):
    '''删除小数点后多余的0'''
    if isinstance(n, int):
        return n
    if isinstance(n, float):
        n = str(n).rstrip('0')  # 删除小数点后多余的0
        n = int(n.rstrip('.')) if n.endswith('.') else float(n)  # 只剩小数点直接转int，否则转回float
        return n
