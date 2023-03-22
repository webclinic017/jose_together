import backtrader as bt
import backtrader.indicators as btind

class PMARInd(bt.Indicator):
    lines = ('pmar',)

    params = (('i_ma_len', 20),
              ('i_ma_type', 'VWMA'),
              ('i_pmarp_lookback',350),
              ('i_ma1Len',5)
              )

    def __init__(self):

        if(self.p.i_ma_type=="VWMA"):
            self.ma = btind.SMA(self.data.close*self.data.volume, period=self.p.i_ma_len) / btind.SMA(self.data.volume, period=self.p.i_ma_len)
        if(self.p.i_ma_type=="EMA"):
            self.ma = btind.EMA(period=self.p.i_ma_len)
        if(self.p.i_ma_type=="SMA"):
            self.ma = btind.SMA(period=self.p.i_ma_len)
        if(self.p.i_ma_type=="WMA"):
            self.ma = btind.WMA(period=self.p.i_ma_len)
        if(self.p.i_ma_type=="HMA"):
            self.ma = btind.HMA(period=self.p.i_ma_len)
        self.lines.pmar = self.data.close/self.ma

