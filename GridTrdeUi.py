import tkinter as tk
from tkinter import ttk


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("网格交易工具")
        self.geometry("860x600")
        self.baseframe = tk.Frame()
        self.baseframe.grid(padx=1,pady=1)
        self.frametop = tk.Frame(self.baseframe,width=500,height=100,)
        self.framecenter = tk.Frame(self.baseframe,width=500, height=450,)
        self.framebttom = tk.Frame(self.baseframe,width=500, height=50,)
        #
        self.framerighttop = tk.Frame(self.baseframe,width=360, height=100, )
        self.framerightcenter = tk.Frame(self.baseframe,width=360, height=450,bg='#B0C4DE')
        self.framerightbottom = tk.Frame(self.baseframe,width=360, height=50)
        #
        # #一个一个frame 的添加
        self.label1 = tk.Label(self.frametop,text='交易货币对：')
        self.label2 = tk.Label(self.frametop, text='设置最高价：')
        self.label3 = tk.Label(self.frametop, text='设置最低价：')
        self.label4 = tk.Label(self.frametop, text='每单套利：')
        self.label5 = tk.Label(self.frametop, text='限额USDT：')
        self.label6 = tk.Label(self.frametop, text='设置网格数量(建议10的倍数)：')
        cv = tk.StringVar()
        self.combbox1 = ttk.Combobox(self.frametop, textvariable=cv,width=8) #下拉框
        self.highpriceEntry = tk.Entry(self.frametop,width=5)
        self.lowpriceEntry = tk.Entry(self.frametop,width=5)
        self.gridnumEntry = tk.Entry(self.frametop, width=5)
        self.rateEntry = tk.Entry(self.frametop, width=5)
        self.limitEntry = tk.Entry(self.frametop, width=5)

        #往frametop 添加标签
        self.label1.grid(row=0,column=0,pady=3,sticky='W')
        self.label2.grid(row=0,column=2,pady=3,sticky='W')
        self.label3.grid(row=0, column=4, pady=3, sticky='W')
        self.label6.grid(row=1, column=0, columnspan=2,padx=2, pady=3, sticky='W')
        self.label4.grid(row=1,column=3,pady=3,sticky='w')
        self.label5.grid(row=1,column=5,pady=3,sticky='w')

        self.combbox1.grid(row=0,column=1,padx=2,pady=2) #x选择货币对
        self.highpriceEntry.grid(row=0,column=3,padx=2,pady=2)
        self.lowpriceEntry.grid(row=0,column=5,padx=2,pady=2)
        self.gridnumEntry.grid(row=1,column=2,padx=2,pady=2)
        self.rateEntry.grid(row=1,column=4,padx=2,pady=2)
        self.limitEntry.grid(row=1,column=6,padx=2,pady=2)
        #  加载滚动条
        self.scrollBar = tk.Scrollbar(self.framecenter,orient='vertical')

        #往framecenter 中添加表格
        self.treetable = ttk.Treeview(self.framecenter,height=24,show='headings',yscrollcommand=self.scrollBar.set)
        self.treetable["columns"] = ("货币对", "结单时间", "结单金额", "结单收益",'币','%')
        self.scrollBar['command']=self.treetable.yview()
        self.treetable.column("货币对", width=100)
        self.treetable.column("结单时间", width=100)
        self.treetable.column("结单金额", width=100)
        self.treetable.column("结单收益", width=100)
        self.treetable.column("币", width=100)
        self.treetable.column("%", width=100)
        self.treetable.heading('货币对',text='货币对')
        self.treetable.heading('结单时间',text='结单时间')
        self.treetable.heading('结单金额',text='结单金额')
        self.treetable.heading('结单收益',text='结单收益')
        self.treetable.heading('币',text='币')
        self.treetable.heading('%',text='%')
        self.treetable.insert("", 0, values=("ETC_USDT", "2021-04-20 18:49:54", "32.457", "0.512","USDT","2.3%"))
        self.treetable.grid(row=0,column=0,padx=2,pady=2,sticky='ns')
        self.scrollBar.grid(row=0,column=1,sticky='ns')
        #3

        #往framebttom 添加东西
        self.exportbutton =tk.Button(self.framebttom,text="导出",width=8,fg='#DDA0DD')
        self.exportbutton.grid(row=0,column=0,padx=2,pady=1,sticky='w')
        self.lablel7 =tk.Label(self.framebttom,text="所有合计利润",bg='#778899',width=15)
        self.lablel8 =tk.Label(self.framebttom,text="234.87 ",bg='yellow',fg='blue',width=10)
        self.lablel9 =tk.Label(self.framebttom,text="USDT",bg='#778899',width=10)
        self.lablel10 =tk.Label(self.framebttom,text="成交",width=5)
        self.lablel11 =tk.Label(self.framebttom,text="23",bg='yellow',fg='blue',width=10)
        self.lablel12 =tk.Label(self.framebttom,text="笔",bg='#778899',width=3)

        self.lablel7.grid(row=0,column=1,padx=2,pady=1)
        self.lablel8.grid(row=0,column=2,padx=2,pady=1)
        self.lablel9.grid(row=0,column=3,padx=2,pady=1)
        self.lablel10.grid(row=0,column=4,padx=2,pady=1)
        self.lablel11.grid(row=0,column=5,padx=2,pady=1)
        self.lablel12.grid(row=0,column=6,padx=2,pady=1)

        #往右边上方添加东西
        self.label13 = tk.Label(self.framerighttop,text='平台设置')
        self.label13.grid(row=0,column=0,padx=2,pady=2)
        cv2 = tk.StringVar()

        self.plantcommbox=ttk.Combobox(self.framerighttop,textvariable=cv2,width=5)
        self.plantcommbox.grid(row=0,column=1,padx=2,pady=2)

        self.APIbutton =tk.Button(self.framerighttop,text='API设置')
        self.APIbutton.grid(row=0,column=2,padx=2,pady=2)

        self.label14 = tk.Label(self.framerighttop, text='选择币种', )
        self.label14.grid(row=1, column=0, padx=2, pady=2)
        cv3 = tk.StringVar()
        self.coincommbox = ttk.Combobox(self.framerighttop, textvariable=cv3,width=5)
        self.coincommbox.grid(row=1, column=1, padx=2, pady=2)

        self.Coinbutton = tk.Button(self.framerighttop, text='添加币种>>')
        self.Coinbutton.grid(row=1, column=2, padx=2, pady=2)

        #往右边中间添加文本log
        #  加载滚动条
        self.yscrollBar = tk.Scrollbar(self.framerightcenter, orient='vertical')
        self.xscrollBar = tk.Scrollbar(self.framerightcenter, orient='horizontal')

        # 添加文本框
        self.textArea = tk.Text(self.framerightcenter,height=33,width=29,yscrollcommand=self.yscrollBar.set,
                                xscrollcommand=self.xscrollBar.set,wrap='none')
        self.yscrollBar['command'] = self.textArea.yview()
        self.xscrollBar['command'] = self.textArea.xview()

        self.textArea.grid(row=0,column=0,padx=1,pady=1,sticky='w')
        self.yscrollBar.grid(row=0,column=1,padx=1,pady=1,sticky='ns')
        self.xscrollBar.grid(row=1, column=0, padx=1, pady=1, sticky='w')

        # 添加启动和停止按钮
        self.startButton = tk.Button(self.framerightbottom,text='启动机器人',fg='red')
        self.stopButton= tk.Button(self.framerightbottom,text='停止',width=8,fg='green')

        self.startButton.grid(row=0,column=0,padx=3,pady=5,sticky='w')
        self.stopButton.grid(row=0,column=1,padx=45,pady=5,sticky='E')



        #整个大的布局分布
        self.frametop.grid(row=0,column=0,padx=1,pady=2)
        self.framecenter.grid(row=1,column=0,padx=3,pady=3,sticky='w')
        self.framebttom.grid(row=2,column=0,padx=2,pady=2,sticky='w')
        self.framerighttop.grid(row=0, column=1,padx=2, pady=2,sticky='w')
        self.framerightcenter.grid(row=1, column=1,padx=2, pady=2,sticky='w')
        self.framerightbottom.grid(row=2, column=1,padx=2, pady=2,sticky='w')




if __name__ =='__main__':
    application = Application()
    application.mainloop()