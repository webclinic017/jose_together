import backtrader as bt
import backtrader.indicators as btind
from Strategies.Indicators.Bbwp import BBWPInd
from Strategies.Indicators.Pmarp import PMARPInd

variation_list_Strategy_100=[
  {'use_daily_filter':False,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'pmarp_exit_level':75},
  {'use_daily_filter':True,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'pmarp_exit_level':75},
  {'use_daily_filter':False,'pamrp_entry_bellow':False,'pamrp_entry_level':70,'bbwp_entry_level':40,'pmarp_exit_level':85},
  {'use_daily_filter':True,'pamrp_entry_bellow':False,'pamrp_entry_level':70,'bbwp_entry_level':40,'pmarp_exit_level':85},
  {'use_daily_filter':False,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'bbwp_entry_level':40,'pmarp_exit_level':85},
  {'use_daily_filter':True,'pamrp_entry_bellow':True,'pamrp_entry_level':15,'bbwp_entry_level':40,'pmarp_exit_level':85}
]


class Strategy_100(bt.Strategy):
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
        self.lastchecktime=None
    def log(self, txt, dt=None):
        if(self.p.debug):
            ''' Logging function fot this strategy'''
            dt = dt or self.datas[0].datetime.datetime(0)
            print('%s, %s' % (dt.isoformat(), txt))
    def next(self, dt=None):
        dt = dt or self.datas[0].datetime.datetime(0)
        if(self.lastchecktime==self.datas[0].datetime.datetime(0)):
            return
        self.lastchecktime = self.datas[0].datetime.datetime(0)
        #condition
        self.log('d:%s %s %s' % (self.fast_ema_daily[0],self.slow_ema_daily[0],self.datas[0].close[0]))
