import time
from datetime import datetime,timedelta
import backtrader as bt
import backtrader.indicators as btind
from ccxtbt import CCXTFeed
from backtrader_plotting import Bokeh

from Strategies.Strategy_2 import Strategy_2,variation_list_Strategy_2
from Strategies.Strategy_3 import Strategy_3,variation_list_Strategy_3
from Strategies.Strategy_4 import Strategy_4,variation_list_Strategy_4
from Strategies.Strategy_5 import Strategy_5,variation_list_Strategy_5
from Strategies.Strategy_8 import Strategy_8,variation_list_Strategy_8
from Strategies.Strategy_9 import Strategy_9,variation_list_Strategy_9
from Strategies.Strategy_10 import Strategy_10,variation_list_Strategy_10
from Strategies.Strategy_11 import Strategy_11,variation_list_Strategy_11
from Strategies.Strategy_13 import Strategy_13,variation_list_Strategy_13
from Strategies.Strategy_14 import Strategy_14,variation_list_Strategy_14

from Strategies.Strategy_100 import Strategy_100,variation_list_Strategy_100

import backtrader.analyzers as btanalyzers
import pandas as pd

def main(strategyNumber,debug):

   startbalance = 100000.0
   commission = 0.0003
   maxbars = 5000 if debug else 50000
   percents_equity = 1

   totals = 0

   variation_list=None
   Strategy = None

   if(strategyNumber==2):
      variation_list=variation_list_Strategy_2
      Strategy = Strategy_2
   if(strategyNumber==3):
      variation_list=variation_list_Strategy_3
      Strategy = Strategy_3
   if(strategyNumber==4):
      variation_list=variation_list_Strategy_4
      Strategy = Strategy_4
   if(strategyNumber==5):
      variation_list=variation_list_Strategy_5
      Strategy = Strategy_5
   if(strategyNumber==8):
      variation_list=variation_list_Strategy_8
      Strategy = Strategy_8
   if(strategyNumber==9):
      variation_list=variation_list_Strategy_9
      Strategy = Strategy_9
   if(strategyNumber==10):
      variation_list=variation_list_Strategy_10
      Strategy = Strategy_10
   if(strategyNumber==11):
      variation_list=variation_list_Strategy_11
      Strategy = Strategy_11
   if(strategyNumber==12):
      variation_list=variation_list_Strategy_12
      Strategy = Strategy_12
   if(strategyNumber==13):
      variation_list=variation_list_Strategy_13
      Strategy = Strategy_13
   if(strategyNumber==14):
      variation_list=variation_list_Strategy_14
      Strategy = Strategy_14
   if(strategyNumber==100):
      variation_list=variation_list_Strategy_100
      Strategy = Strategy_100
   for symbol in ["BTC","ETH","BNB","ADA","XRP","LDO","SOL","MATIC","DOGE","SAND"]:
      for currentTF in [15,5,30,60,120,240,360]:
         variation_index = 0
         for params in variation_list:
            variation_index = variation_index + 1
            print('--strategyNumber %s symbol %s currentTF %s variation_index %s---'  %( strategyNumber,symbol,currentTF,variation_index))
            params["percents_equity"] = percents_equity
            params["debug"] = debug
            cerebro = bt.Cerebro(cheat_on_open=True)
            cerebro.broker.setcommission(commtype=bt.CommInfoBase.COMM_PERC,commission=commission)
            cerebro.addstrategy(Strategy,params)

            cerebro.addanalyzer(btanalyzers.DrawDown, _name='drawdown')
            cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='trade')

            #prepare feed
            fromdate = datetime.now()-timedelta(minutes=currentTF*maxbars)
            todate = datetime.now()
            
            data1 = CCXTFeed(exchange='binance',
                                   dataname=symbol+'BUSD',
                                   timeframe=bt.TimeFrame.Minutes,
                                   fromdate=fromdate,
                                   todate=todate,
                                   compression=currentTF,
                                   ohlcv_limit=5000,
                                   currency=symbol,
                                   retries=5,
                                   historical=True,
                                   drop_newest=True,
                                   config={
                                      'enableRateLimit': True,
                                      'options': {'defaultType': 'future'}})
            cerebro.adddata(data1)

            data2 = CCXTFeed(exchange='binance',
                                   dataname=symbol+'BUSD',
                                   timeframe=bt.TimeFrame.Days,
                                   fromdate=fromdate-timedelta(days=200),
                                   todate=todate,
                                   compression=1,
                                   ohlcv_limit=500,
                                   currency=symbol,
                                   retries=5,
                                   historical=True,
                                   config={
                                      'enableRateLimit': True,
                                      'options': {'defaultType': 'future'}})
            cerebro.adddata(data2)
            cerebro.broker.setcash(startbalance)
            thestrats = cerebro.run(runonce=False)
            b = Bokeh(style='bar', plot_mode='multi',filename='figure/%s_%s_%s_%s.html' %(strategyNumber,symbol,currentTF,variation_index))
            cerebro.plot(b)

            thestrat = thestrats[0]
            dd = thestrat.analyzers.drawdown.get_analysis()
            trade = thestrat.analyzers.trade.get_analysis()
            mdd = round(dd.max.drawdown,2)
            if(trade.total.total>0):
               netprofit = round(trade.pnl.net.total,2)
               profit_percent= round(trade.pnl.net.total/startbalance*100,2)
               win_trades = trade.won.total
               loss_trades = trade.lost.total
               winrate = 0 if (win_trades+loss_trades==0) else round(win_trades/(win_trades+loss_trades)*100,2)

               profit_average=round(trade.won.pnl.average,2)
               profit_max=round(trade.won.pnl.max,2)
               loss_average=round(-trade.lost.pnl.average,2)
               loss_max=round(-trade.lost.pnl.max,2)
               gross_profit = round(trade.won.pnl.total,2)
               gross_loss = round(-trade.lost.pnl.total,2)
               profit_factor = round(gross_profit/gross_loss,2) if(gross_loss>0) else None
               p_matrix = {
                 "totals":[totals],
                 "symbol":[symbol+'BUSDPerp'],
                 "tf":[currentTF],
                 "variation":[variation_index],
                 "netprofit": [netprofit],
                 "profit_percent(%)": [profit_percent],
                 "MDD(%)": [mdd],
                 "win trades": [win_trades],
                 "loss trades": [loss_trades],
                 "winrate": [winrate],
                 "W.Avg": [profit_average],
                 "W.Max": [profit_max],
                 "L.Avg": [loss_average],
                 "L.Max": [loss_max],
                 "GrossProfit": [gross_profit],
                 "GrossLoss": [gross_loss],
                 "ProfitFactor": [profit_factor]
               }
               newdf = pd.DataFrame(p_matrix)
               if(totals==0):
                  df = newdf
               else:
                  df=pd.concat([df,newdf])
               print('profit %s---'  %( netprofit))
            totals = totals +1
            if(debug):
               break
         if(debug):
            break
      if(debug):
         break
   df.to_csv('./result/out'+str(strategyNumber)+'.csv')
   print("Completed")

debug=True

for strategyNumber in [2,3,4,5,8,9,10,11,13,14]:
   main(strategyNumber,debug)


