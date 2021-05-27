from django.db import models

# Create your models here.
#创建使用列表
class User_info(models.Model):
    '''
    使用者的账户
    '''
    Uid =models.AutoField(primary_key=True)
    Uniqueid = models.CharField(max_length=12,verbose_name='随机生成的用户随机编号')
    ak = models.CharField(max_length=12,verbose_name='用户的appkey')
    sk =models.CharField(max_length=18,verbose_name='用户的screatkey')
    tradeplant = models.CharField(max_length=5,verbose_name='交易所')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')


#创建任务列表
class Task_info(models.Model):
    '''
    创建任务列表
    '''
    Tid = models.AutoField(primary_key=True)
    Uniqueid = models.CharField(max_length=12,verbose_name='用户随机编号')
    TaskName = models.CharField(max_length=12,verbose_name="任务名称")
    TradePlantName = models.CharField(max_length=10,verbose_name='交易所名称')
    CoinExchange =  models.CharField(max_length=8,verbose_name='交易对名称')
    HighestPrice = models.CharField(max_length=8,verbose_name='最高价格')
    lowestPrice = models.CharField(max_length=8,verbose_name='最低价格')
    lockNum = models.CharField(max_length=8,verbose_name='准备使用的Usdt个数')
    gridnum = models.CharField(max_length=8,verbose_name="网格数量")
    trate = models.CharField(max_length=8,verbose_name="每单利润")
    task_flag = models.CharField(max_length=1, verbose_name='有效标记，0-失效，1-有效')
    create_date = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updatedate = models.CharField(max_length=15,blank=None, verbose_name='更新时间')


# 收益列表
class CompleteOrdertb(models.Model):
    '''
    完整的单子记录
    '''
    CoId = models.AutoField(primary_key=True)
    CoinPair = models.CharField(max_length=8,verbose_name='交易货币对')
    UserUniqkey = models.CharField(max_length=12,verbose_name='用户唯一编号')
    Bidorderid = models.CharField(max_length=12,verbose_name='买单的orderid')
    Bidprice = models.DecimalField(max_digits=6,decimal_places=6,verbose_name='买单的价格')
    Bidqulity = models.DecimalField(max_digits=5,decimal_places=4,verbose_name='买单的数量')
    BidAmount = models.DecimalField(max_digits=6,decimal_places=4,verbose_name='买单的成交金额')
    BidCreateTime = models.CharField(max_length=20,verbose_name='买单创建时间')
    Askorderid = models.CharField(max_length=12, verbose_name='卖单的orderid')
    Askprice = models.DecimalField(max_digits=6, decimal_places=6, verbose_name='卖单的价格')
    Askqulity = models.DecimalField(max_digits=5, decimal_places=4, verbose_name='卖单的数量')
    AskAmount = models.DecimalField(max_digits=6, decimal_places=4, verbose_name='卖单的成交金额')
    AskCreateTime = models.CharField(max_length=20, verbose_name='卖单创建时间')
    OrderProfit = models.DecimalField(max_digits=6,decimal_places=5, verbose_name='本单收益')
    OrderProfitrate = models.DecimalField(max_digits=5,decimal_places=4, verbose_name='本单收益率')


# 运行任务状态
class TaskRuninfo(models.Model):
    '''
    任务的运行状态
    '''
    Id= models.AutoField(primary_key=True)
    Uniqueid = models.CharField(max_length=12, verbose_name='用户随机编号')
    taskid = models.CharField(max_length=4,verbose_name='任务的id')
    TaskName = models.CharField(max_length=12, verbose_name="任务名称")
    taskstarttime = models.CharField(max_length=15,blank=None,verbose_name='启动时间')
    flag = models.CharField(max_length=1, verbose_name='运行标记，0-停止，1-运行中')
    taskstoptime  = models.CharField(max_length=15,blank=None,verbose_name='停止时间')


#平台信息base表
class TradePlant(models.Model):
    '''
    交易平台的信息
    '''
    Id = models.AutoField(primary_key=True)
    plantName = models.CharField(max_length=10, verbose_name="交易所名称")
    plantApiHost = models.CharField(max_length=20,verbose_name="交易所Api地址")
    createTime = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')







