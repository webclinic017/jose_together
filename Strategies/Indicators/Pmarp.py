import backtrader as bt
import backtrader.indicators as btind

class PMARPInd(bt.Indicator):
    lines = ('pmarp','pmarpma')

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

    def next(self):
        _pmarpSum = 0.0
        if len(self.pmar)<self.p.i_pmarp_lookback+1:
            _len = len(self.pmar)-1
        else:
            _len = self.p.i_pmarp_lookback
        for _i in range(1,_len+1):
            _pmarpSum += ( 0 if self.pmar[-_i]>self.pmar[0] else 1 )
        
        self.lines.pmarp[0] = ( _pmarpSum / _len)*100 if (len(self) >= self.p.i_ma_len) else None

        _pmarpmaSum = 0.0
        if len(self.lines.pmarp)<self.p.i_ma1Len+1:
            _lenma = len(self.self.lines.pmarp)-1
        else:
            _lenma = self.p.i_ma1Len
        for _i in range(0,_lenma):
            _pmarpmaSum += self.lines.pmarp[-_i]

        self.lines.pmarpma[0] = ( _pmarpmaSum / _lenma)        