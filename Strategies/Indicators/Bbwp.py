import backtrader as bt
import backtrader.indicators as btind

class BBWPInd(bt.Indicator):
    lines = ('bbwp','bbwpma')

    params = (('i_bbwpLen', 13),
              ('i_bbwpLkbk', 252),
              ('i_basisType', 'SMA'),
              ('i_ma1Len',5)
              )

    def __init__(self):
        if(self.p.i_basisType=="EMA"):
            self._basis = btind.EMA(self.data.close,period=self.p.i_bbwpLen)
        if(self.p.i_basisType=="SMA"):
            self._basis = btind.SMA(self.data.close,period=self.p.i_bbwpLen)
        if(self.p.i_basisType=="WMA"):
            self._basis = btind.WMA(self.data.close,period=self.p.i_bbwpLen)
        if(self.p.i_basisType=="HMA"):
            self._basis = btind.HMA(self.data.close,period=self.p.i_bbwpLen)
        self._dev = btind.StdDev(self.data.close,period=self.p.i_bbwpLen)
        self._bbw = ( self._basis + self._dev - ( self._basis - self._dev )) / self._basis

    def next(self):
        _bbwSum = 0.0
        if len(self._bbw)<self.p.i_bbwpLkbk+1:
            _len = len(self._bbw)-1
        else:
            _len = self.p.i_bbwpLkbk
        for _i in range(1,_len+1):
            _bbwSum += ( 0 if self._bbw[-_i]>self._bbw[0] else 1 )



        self.lines.bbwp[0] = ( _bbwSum / _len)*100 if (len(self) >= self.p.i_bbwpLen) else None


        _bbwmaSum = 0.0
        if len(self.lines.bbwp)<self.p.i_ma1Len+1:
            _lenma = len(self.self.lines.bbwp)-1
        else:
            _lenma = self.p.i_ma1Len
        for _i in range(0,_lenma):
            _bbwmaSum += self.lines.bbwp[-_i]

        self.lines.bbwpma[0] = ( _bbwmaSum / _lenma)