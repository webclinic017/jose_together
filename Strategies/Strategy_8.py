import backtrader as bt
import backtrader.indicators as btind
from Strategies.Indicators.Bbwp import BBWPInd
from Strategies.Indicators.Pmarp import PMARPInd

#8 Downtrend Momentum Short Scalp
# TF – 15m
# Indicators –
#     21 and 55 EMA 
# Stochastic (14,3,6)
#     PMARP   
# SL1 – Close above entry range wick high
# SL2 – Wick above prior high
# Entry 
#     21EMA < 55EMA
#     Stochastic > 70
#     %D > 70 on turndown
#     Entry on turndown
    
# Exit
# PMARP < 15
    
# Report variations
#     Daily 21EMA < 55 EMA
# PMARP < 20
# 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, D


variation_list_Strategy_8=[
  {'use_daily_filter':False,'pmarp_exit_level':15},
  {'use_daily_filter':False,'pmarp_exit_level':20},
  {'use_daily_filter':True,'pmarp_exit_level':15},
  {'use_daily_filter':True,'pmarp_exit_level':20},

]


class Strategy_8(bt.Strategy):
    params = (
        ('percents_equity',1),
        ('sto_entry_level',70),
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
        self.slow_ema_daily = btind.EMA(self.data1,period=self.p.slow_ema_period)
        self.fast_ema_daily = btind.EMA(self.data1,period=self.p.fast_ema_period)
        self.pmarp = PMARPInd(i_ma_len=self.p.i_ma_len,i_ma_type=self.p.i_ma_type,i_pmarp_lookback=self.p.i_pmarp_lookback)
        self.sto = btind.StochasticSlow()#percK,percD

        self.SL1 = None
        self.SL2 = None
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
                self.barsAfterEnter = -1
                self.log('SELL EXECUTED, %.2f %.2f' % (order.executed.price,self.datas[0].high[0]))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def getLotSize(self):
        return self.broker.get_cash()*self.p.percents_equity/100/self.datas[0].close[0]

    def next(self, dt=None):
        
        #realtime
        dt = dt or self.datas[0].datetime.datetime(0)
        #condition
        short_entry_condition = self.fast_ema[0]<self.slow_ema[0] and \
            self.sto.percD[0]>self.p.sto_entry_level and \
            self.sto.percD[0]<self.sto.percD[-1] and \
            (self.p.use_daily_filter==False or self.fast_ema_daily[0]<self.slow_ema_daily[0])

        short_exit_condition = self.pmarp.pmarp[0]<self.p.pmarp_exit_level

        if(not self.position or self.position.size<0):
            self.barsAfterEnter = self.barsAfterEnter+1

        if((not self.position or self.position.size==0) and short_entry_condition ):
            self.size = self.getLotSize()
            self.sell(size=self.size)
            self.SL1=self.datas[0].high[0]
            self.SL2=None

            self.log('initiated order ,stoploss SL1 %s' % (self.SL1))
        else:
            if((self.positions and self.position.size<0)):
                if(self.barsAfterEnter>1):
                    if(self.SL2 is None or self.SL2>self.datas[0].high[-1]):
                        self.SL2 = self.datas[0].high[-1]
                        if(self.stoporder is None):
                            self.log('set sl2 to %s %s' % (self.barsAfterEnter,self.SL2))
                            self.stoporder = self.buy(exectype=bt.Order.Stop, price=self.SL2,size=self.size)
                        else:
                            self.log('SL2 modified to %s' % self.SL2)
                            self.stoporder.created.price = self.SL2

                if(short_exit_condition or  (self.SL1 and self.datas[0].close[0]>self.SL1)):
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
