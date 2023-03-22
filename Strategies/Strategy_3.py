import backtrader as bt
import backtrader.indicators as btind
from Strategies.Indicators.Bbwp import BBWPInd
from Strategies.Indicators.Pmarp import PMARPInd

variation_list_Strategy_3=[
  {'use_daily_filter':False,'bbwp_entry_level':35,'pmarp_exit_level':15},
  {'use_daily_filter':False,'bbwp_entry_level':35,'pmarp_exit_level':20},
  {'use_daily_filter':False,'bbwp_entry_level':35,'pmarp_exit_level':25},
  {'use_daily_filter':False,'bbwp_entry_level':40,'pmarp_exit_level':15},
  {'use_daily_filter':False,'bbwp_entry_level':40,'pmarp_exit_level':20},
  {'use_daily_filter':False,'bbwp_entry_level':40,'pmarp_exit_level':25},
  {'use_daily_filter':False,'bbwp_entry_level':50,'pmarp_exit_level':15},
  {'use_daily_filter':False,'bbwp_entry_level':50,'pmarp_exit_level':20},
  {'use_daily_filter':False,'bbwp_entry_level':50,'pmarp_exit_level':25},
  {'use_daily_filter':True,'bbwp_entry_level':35,'pmarp_exit_level':15},
  {'use_daily_filter':True,'bbwp_entry_level':35,'pmarp_exit_level':20},
  {'use_daily_filter':True,'bbwp_entry_level':35,'pmarp_exit_level':25},
  {'use_daily_filter':True,'bbwp_entry_level':40,'pmarp_exit_level':15},
  {'use_daily_filter':True,'bbwp_entry_level':40,'pmarp_exit_level':20},
  {'use_daily_filter':True,'bbwp_entry_level':40,'pmarp_exit_level':25},
  {'use_daily_filter':True,'bbwp_entry_level':50,'pmarp_exit_level':15},
  {'use_daily_filter':True,'bbwp_entry_level':50,'pmarp_exit_level':20},
  {'use_daily_filter':True,'bbwp_entry_level':50,'pmarp_exit_level':25}
]


class Strategy_3(bt.Strategy):
    params = (
        ('percents_equity',1),
        ('bbwp_entry_level',35),
        ('pmarp_exit_level',15),
        ('use_daily_filter',False),
        ('fast_ema_period', 21),
        ('slow_ema_period', 55),
        ('i_bbwpLen', 13),
        ('i_bbwpLkbk', 252),
        ('i_basisType', 'SMA'),
        ('i_ma_len', 20),
        ('i_ma_type', 'VWMA'),
        ('i_pmarp_lookback',350),
        ('debug',True),
    )

    def __init__(self, params=None):
        if params != None:
            for name, val in params.items():
                setattr(self.params, name, val)        
        self.next_runs = 0
        self.slow_ema = btind.EMA(period=self.p.slow_ema_period)
        self.fast_ema = btind.EMA(period=self.p.fast_ema_period)
        self.bbwp = BBWPInd(i_bbwpLen=self.p.i_bbwpLen,i_bbwpLkbk=self.p.i_bbwpLkbk,i_basisType=self.p.i_basisType)
        self.pmarp = PMARPInd(i_ma_len=self.p.i_ma_len,i_ma_type=self.p.i_ma_type,i_pmarp_lookback=self.p.i_pmarp_lookback)
        self.bbwp_daily = BBWPInd(self.data1,i_bbwpLen=self.p.i_bbwpLen,i_bbwpLkbk=self.p.i_bbwpLkbk,i_basisType=self.p.i_basisType)
        
        self.SL1 = None
        self.SL2 = None
        self.limitorder = None
        self.stoporder = None
        self.size=0
        self.lastchecktime = None
        self.barsAfterEnter = 0

    def log(self, txt, dt=None):
        if(self.p.debug):
            ''' Logging function fot this strategy'''
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
                self.stoporder = None
            elif order.issell():
                self.limitorder = None
                self.barsAfterEnter = -1
                self.log('SELL EXECUTED, %.2f %.2f' % (order.executed.price,self.datas[0].high[0]))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.limitorder =None
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
    
    def next(self, dt=None):

        isBarclose = True
        dt = dt or self.datas[0].datetime.datetime(0)
        if(self.lastchecktime==self.datas[0].datetime.datetime(-1)):
            isBarclose = False
        self.lastchecktime = self.datas[0].datetime.datetime(-1)

        #condition
        short_entry_condition = self.fast_ema[0]<self.slow_ema[0] and \
            self.bbwp[0]<self.p.bbwp_entry_level and \
            (self.p.use_daily_filter==False or self.bbwp_daily.bbwp[0]<self.bbwp_daily.bbwpma[0]) 
        short_exit_condition = self.pmarp.pmarp[0]<self.p.pmarp_exit_level

        if(isBarclose and (not self.position or self.position.size<0)):
            self.barsAfterEnter = self.barsAfterEnter+1

        if(isBarclose and (not self.position or self.position.size==0) and (self.limitorder is None) and short_entry_condition ):
            if(self.datas[0].close[0]<self.slow_ema[0]):
                if(self.limitorder is not None):
                    self.log('Limit order modified %s' % (self.slow_ema[0]))
                    self.limitorder.created.price = self.slow_ema[0]
                else:
                    self.size = self.broker.get_cash()*self.p.percents_equity/100/self.datas[0].close[0]
                    self.limitorder=self.sell(size=self.size,price =self.slow_ema[-1],exectype=bt.Order.Limit)
                    self.SL1=None
                    self.SL2=None
                    self.log('initiated limit order at %s stoploss %s' % (self.datas[0].close[0],self.datas[0].high[0]))
        else:
            if(self.limitorder is not None and isBarclose):
                if(short_exit_condition):
                    self.log('Cancel limit order')
                    if(self.broker.cancel(self.limitorder)==False):
                        return
                    self.limitorder=None
            else:
                if((self.positions and self.position.size<0)):
                    if(self.barsAfterEnter>0):
                        if(self.SL1 is None and isBarclose):
                            self.SL1  = self.datas[0].high[-self.barsAfterEnter]
                            self.log('set sl1 to %s' % (self.SL1))
                        if(self.barsAfterEnter>1):

                            if((self.SL2 is None or self.SL2>self.datas[0].high[-1]) and isBarclose):
                                self.SL2 = self.datas[0].high[-1]
                                self.log('set sl2 to %s %s' % (self.barsAfterEnter,self.SL2))
                                if(self.stoporder is None):
                                    self.log('stoploss order initiated')
                                    self.stoporder = self.buy(exectype=bt.Order.Stop, price=self.SL2,size=self.size)
                                else:
                                    self.stoporder.created.price = self.SL2
                    if(isBarclose and short_exit_condition or  (self.SL1 and self.datas[0].close[0]>self.SL1)):
                        if(short_exit_condition):
                            self.log('hit sl1 stoploss %s close %s' % (self.SL1,self.datas[0].close[0]))
                        else:
                            self.log('exit condition met')
                        if(self.stoporder is not None):
                            cancelResult = self.broker.cancel(self.stoporder)
                            self.log('Cancel stoploss order %s' % cancelResult)
                            if(cancelResult==False):
                                self.log('Failed to cancel stoploss order')
                                return
                            self.stoporder=None
                        self.close()
