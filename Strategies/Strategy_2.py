import backtrader as bt
import backtrader.indicators as btind
from Strategies.Indicators.Bbwp import BBWPInd
from Strategies.Indicators.Pmarp import PMARPInd

variation_list_Strategy_2=[
  {'use_daily_filter':False,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'pmarp_exit_level':75},
  {'use_daily_filter':True,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'pmarp_exit_level':75},
  {'use_daily_filter':False,'pamrp_entry_bellow':False,'pamrp_entry_level':70,'bbwp_entry_level':40,'pmarp_exit_level':85},
  {'use_daily_filter':True,'pamrp_entry_bellow':False,'pamrp_entry_level':70,'bbwp_entry_level':40,'pmarp_exit_level':85},
  {'use_daily_filter':False,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'bbwp_entry_level':40,'pmarp_exit_level':85},
  {'use_daily_filter':True,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'bbwp_entry_level':40,'pmarp_exit_level':85}
]

class Strategy_2(bt.Strategy):
    params = (
        ('percents_equity',1),
        ('pamrp_entry_level',15),
        ('pamrp_entry_bellow',True),
        ('bbwp_entry_level',35),
        ('pmarp_exit_level',75),
        ('use_daily_filter',False),
        ('fast_ema_period', 21),
        ('slow_ema_period', 55),
        ('i_bbwpLen', 13),
        ('i_bbwpLkbk', 252),
        ('i_basisType', 'SMA'),
        ('i_ma_len', 20),
        ('i_ma_type', 'VWMA'),
        ('i_pmarp_lookback',350),
        ('debug',False),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items():
                setattr(self.params, name, val)        
        self.next_runs = 0
        self.slow_ema = btind.EMA(period=self.p.slow_ema_period)
        self.fast_ema = btind.EMA(period=self.p.fast_ema_period)
        self.fast_ema_daily = btind.EMA(self.data1,period=self.p.fast_ema_period)
        self.slow_ema_daily = btind.EMA(self.data1,period=self.p.slow_ema_period)
        self.bbwp = BBWPInd(i_bbwpLen=self.p.i_bbwpLen,i_bbwpLkbk=self.p.i_bbwpLkbk,i_basisType=self.p.i_basisType)
        self.pmarp = PMARPInd(i_ma_len=self.p.i_ma_len,i_ma_type=self.p.i_ma_type,i_pmarp_lookback=self.p.i_pmarp_lookback)
        self.stoploss =None
        self.stoporder = None
        self.size=0
        self.trades =0 
        self.lastchecktime = None
    def log(self, txt, dt=None):
        if(self.p.debug):
            ''' Logging function fot this strategy'''
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f %.2f %.2f' % (order.executed.price,order.size,self.size))
                self.stoporder = self.sell(exectype=bt.Order.Stop, price=self.stoploss,size=self.size)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f %.2f' % (order.executed.price,order.size))
                self.stoporder = None
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)

        if(self.lastchecktime==self.datas[0].datetime.datetime(0)):
            return
        self.lastchecktime = self.datas[0].datetime.datetime(0)
        
        #condition
        long_entry_condition = self.fast_ema[0]>self.slow_ema[0] and \
            (self.p.use_daily_filter==False or self.fast_ema_daily[0]>self.slow_ema_daily[0]) and \
            self.bbwp.bbwp[0]<self.p.bbwp_entry_level and \
            (self.p.pamrp_entry_bellow and self.pmarp.pmarp[0]<self.p.pamrp_entry_level or \
            self.p.pamrp_entry_bellow==False and self.pmarp.pmarp[0]>self.p.pamrp_entry_level)
        if(long_entry_condition):
            self.log('good long condition %s %s' % (self.datas[0].close[0],self.position.size))    
        long_exit_condition = self.pmarp.pmarp[0]>self.p.pmarp_exit_level
        if((not self.position or self.position.size==0) and (self.stoporder is None) and long_entry_condition):
            self.size = self.broker.get_cash()*self.p.percents_equity/100/self.datas[0].close[0]
            order=self.buy(size=self.size)
            self.log('buy at %s, stoploss at %s ' %(self.datas[0].close[0],self.datas[0].low[0]))
            self.stoploss = self.datas[0].low[0]
            self.trades = self.trades+1
        else:
            if(self.positions and self.position.size>0):
                if(long_exit_condition):
                    if(self.stoporder is not None):
                        cancelResult = self.broker.cancel(self.stoporder)
                        if(cancelResult==False):
                            return
                        self.stoporder = None
                    self.log('call close %s' %(self.stoporder))
                    self.close()
                else:
                    if((self.stoporder is not None) and self.stoploss<self.datas[0].low[-1]):
                        self.stoploss = self.datas[0].low[-1]
                        self.stoporder.created.price = self.stoploss
                        self.log('Order modified %s' % self.stoploss)
