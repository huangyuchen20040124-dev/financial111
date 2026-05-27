# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 00:14:26 2026

@author: user
"""

#%%
###### 載入必要模組
from order_Lo8 import Record
import numpy as np
from talib.abstract import SMA, EMA, WMA, RSI, BBANDS, MACD, STOCH
import datetime, indicator
import pandas as pd


#%%
###### 資料讀入與前處理
df = pd.read_excel("kbars_2330_2022-01-01-2024-04-09.xlsx", index_col=0)
df.columns
df.head()


#%%
###### 畫 KBar 圖
df.set_index("time", inplace=True)
import mplfinance as mpf
mpf.plot(df, volume=True, addplot=[], type='candle', style='charles')
df['time'] = df.index


#%%
###### 轉化為字典
KBar_dic = df.to_dict()

KBar_open_list = list(KBar_dic['open'].values())
KBar_dic['open'] = np.array(KBar_open_list).astype(np.float64)

KBar_dic['product'] = np.repeat('tsmc', KBar_dic['open'].size)

KBar_time_list = list(KBar_dic['time'].values())
KBar_time_list = [i.to_pydatetime() for i in KBar_time_list]
KBar_dic['time'] = np.array(KBar_time_list)

KBar_low_list = list(KBar_dic['low'].values())
KBar_dic['low'] = np.array(KBar_low_list).astype(np.float64)

KBar_high_list = list(KBar_dic['high'].values())
KBar_dic['high'] = np.array(KBar_high_list).astype(np.float64)

KBar_close_list = list(KBar_dic['close'].values())
KBar_dic['close'] = np.array(KBar_close_list).astype(np.float64)

KBar_volume_list = list(KBar_dic['volume'].values())
KBar_dic['volume'] = np.array(KBar_volume_list)

KBar_amount_list = list(KBar_dic['amount'].values())
KBar_dic['amount'] = np.array(KBar_amount_list)


#%%
######  改變 KBar 時間長度
Date = '20220101'
KBar = indicator.KBar(Date, 2880)  ## 2880分鐘=2天

for i in range(KBar_dic['time'].size):
    time = KBar_dic['time'][i]
    price = KBar_dic['close'][i]
    qty = KBar_dic['volume'][i]
    amount = KBar_dic['amount'][i]
    tag = KBar.AddPrice(time, price, qty)

    if tag != 1:
        continue


#%%
###### 形成變換長度後的 KBar 字典
KBar_dic = {}
KBar_dic['time'] = KBar.TAKBar['time']
KBar_dic['product'] = np.repeat('tsmc', KBar_dic['time'].size)
KBar_dic['open'] = KBar.TAKBar['open']
KBar_dic['high'] = KBar.TAKBar['high']
KBar_dic['low'] = KBar.TAKBar['low']
KBar_dic['close'] = KBar.TAKBar['close']
KBar_dic['volume'] = KBar.TAKBar['volume']


#%%
###### 定義繪製相關圖形之函數
def KbarToDf(KBar_dic):
    Kbar_df = pd.DataFrame(KBar_dic)
    Kbar_df.columns = [i[0].upper() + i[1:] for i in Kbar_df.columns]
    Kbar_df.set_index("Time", inplace=True)
    return Kbar_df


def ChartKBar(KBar_dic, addp=None, volume_enable=True):
    if addp is None:
        addp = []
    Kbar_df = KbarToDf(KBar_dic)
    mpf.plot(Kbar_df, volume=volume_enable, addplot=addp, type='candle', style='charles')


def ChartOrder(KBar_dic, TR, addp=None, volume_enable=True):
    if addp is None:
        addp = []

    Kbar_df = KbarToDf(KBar_dic)

    # 買(多)方下單點位紀錄
    BTR = [i for i in TR if i[0] == 'Buy' or i[0] == 'B']
    BuyOrderPoint = []
    BuyCoverPoint = []

    for date, value in Kbar_df['Close'].items():
        if date in [i[2] for i in BTR]:
            BuyOrderPoint.append(Kbar_df['Low'][date] * 0.999)
        else:
            BuyOrderPoint.append(np.nan)

        if date in [i[4] for i in BTR]:
            BuyCoverPoint.append(Kbar_df['High'][date] * 1.001)
        else:
            BuyCoverPoint.append(np.nan)

    if [i for i in BuyOrderPoint if not np.isnan(i)] != []:
        addp.append(mpf.make_addplot(BuyOrderPoint, scatter=True, markersize=50, marker='^', color='red'))
        addp.append(mpf.make_addplot(BuyCoverPoint, scatter=True, markersize=50, marker='v', color='blue'))

    # 賣(空)方下單點位紀錄
    STR = [i for i in TR if i[0] == 'Sell' or i[0] == 'S']
    SellOrderPoint = []
    SellCoverPoint = []

    for date, value in Kbar_df['Close'].items():
        if date in [i[2] for i in STR]:
            SellOrderPoint.append(Kbar_df['High'][date] * 1.001)
        else:
            SellOrderPoint.append(np.nan)

        if date in [i[4] for i in STR]:
            SellCoverPoint.append(Kbar_df['Low'][date] * 0.999)
        else:
            SellCoverPoint.append(np.nan)

    if [i for i in SellOrderPoint if not np.isnan(i)] != []:
        addp.append(mpf.make_addplot(SellOrderPoint, scatter=True, markersize=50, marker='v', color='green'))
        addp.append(mpf.make_addplot(SellCoverPoint, scatter=True, markersize=50, marker='^', color='pink'))

    ChartKBar(KBar_dic, addp, volume_enable)


def ChartOrder_MA(KBar_dic, TR):
    Kbar_df = KbarToDf(KBar_dic)
    addp = []
    addp.append(mpf.make_addplot(Kbar_df['MA_long'], color='red'))
    addp.append(mpf.make_addplot(Kbar_df['MA_short'], color='yellow'))
    ChartOrder(KBar_dic, TR, addp)


#%%
######  (一) 移動平均線策略

OrderRecord = Record()

LongMAPeriod = 10
ShortMAPeriod = 2
MoveStopLoss = 10

KBar_dic['MA_long'] = SMA(KBar_dic, timeperiod=LongMAPeriod)
KBar_dic['MA_short'] = SMA(KBar_dic, timeperiod=ShortMAPeriod)

Order_Quantity = 3

for n in range(0, len(KBar_dic['time']) - 1):
    if not np.isnan(KBar_dic['MA_long'][n - 1]):

        if OrderRecord.GetOpenInterest() == 0:
            if KBar_dic['MA_short'][n - 1] <= KBar_dic['MA_long'][n - 1] and KBar_dic['MA_short'][n] > KBar_dic['MA_long'][n]:
                OrderRecord.Order('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice - MoveStopLoss
                continue

            if KBar_dic['MA_short'][n - 1] >= KBar_dic['MA_long'][n - 1] and KBar_dic['MA_short'][n] < KBar_dic['MA_long'][n]:
                OrderRecord.Order('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice + MoveStopLoss
                continue

        elif OrderRecord.GetOpenInterest() > 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Sell', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] - MoveStopLoss > StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] - MoveStopLoss
            elif KBar_dic['close'][n] < StopLossPoint:
                OrderRecord.Cover('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], OrderRecord.GetOpenInterest())
                continue

        elif OrderRecord.GetOpenInterest() < 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Buy', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], -OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] + MoveStopLoss < StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] + MoveStopLoss
            elif KBar_dic['close'][n] > StopLossPoint:
                OrderRecord.Cover('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], -OrderRecord.GetOpenInterest())
                continue

ChartOrder_MA(KBar_dic, OrderRecord.GetTradeRecord())
KBar_dic.keys()

print('交易紀錄: \n', OrderRecord.GetTradeRecord())
print('\n')
print('利潤清單(TWD,點數): \n',OrderRecord.GetProfit())
print('\n')
print('淨利(TWD,點數): ',OrderRecord.GetTotalProfit())
print('\n')
print('勝率: ',OrderRecord.GetWinRate())
print('\n')
print('最大連續虧損(TWD,點數): ',OrderRecord.GetAccLoss())
print('\n')
print('最大累計盈虧(TWD,點數)回落: ',OrderRecord.GetMDD())
print('\n')


#%%
###### (二) RSI 順勢策略

OrderRecord = Record()

LongRSIPeriod = 10
ShortRSIPeriod = 5
MoveStopLoss = 30
Order_Quantity = 3

KBar_dic['RSI_long'] = RSI(KBar_dic, timeperiod=LongRSIPeriod)
KBar_dic['RSI_short'] = RSI(KBar_dic, timeperiod=ShortRSIPeriod)
KBar_dic['Middle'] = np.array([50] * len(KBar_dic['time']))

for n in range(1, len(KBar_dic['time']) - 1):
    if not np.isnan(KBar_dic['RSI_long'][n - 1]):
        if OrderRecord.GetOpenInterest() == 0:
            if KBar_dic['RSI_short'][n - 1] <= KBar_dic['RSI_long'][n - 1] and KBar_dic['RSI_short'][n] > KBar_dic['RSI_long'][n] and KBar_dic['RSI_long'][n] > KBar_dic['Middle'][n]:
                OrderRecord.Order('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice - MoveStopLoss
                continue

            if KBar_dic['RSI_short'][n - 1] >= KBar_dic['RSI_long'][n - 1] and KBar_dic['RSI_short'][n] < KBar_dic['RSI_long'][n] and KBar_dic['RSI_long'][n] < KBar_dic['Middle'][n]:
                OrderRecord.Order('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice + MoveStopLoss
                continue

        elif OrderRecord.GetOpenInterest() > 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Sell', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] - MoveStopLoss > StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] - MoveStopLoss
            elif KBar_dic['close'][n] < StopLossPoint:
                OrderRecord.Cover('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], OrderRecord.GetOpenInterest())
                continue

        elif OrderRecord.GetOpenInterest() < 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Buy', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], -OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] + MoveStopLoss < StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] + MoveStopLoss
            elif KBar_dic['close'][n] > StopLossPoint:
                OrderRecord.Cover('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], -OrderRecord.GetOpenInterest())
                continue

# OrderRecord.GetTradeRecord()
# OrderRecord.GetProfit()
# OrderRecord.GetTotalProfit()
# OrderRecord.GetWinRate()
# OrderRecord.GetAccLoss()
# OrderRecord.GetMDD()
print('交易紀錄: \n', OrderRecord.GetTradeRecord())
print('\n')
print('利潤清單(TWD,點數): \n',OrderRecord.GetProfit())
print('\n')
print('淨利(TWD,點數): ',OrderRecord.GetTotalProfit())
print('\n')
print('勝率: ',OrderRecord.GetWinRate())
print('\n')
print('最大連續虧損(TWD,點數): ',OrderRecord.GetAccLoss())
print('\n')
print('最大累計盈虧(TWD,點數)回落: ',OrderRecord.GetMDD())
print('\n')
OrderRecord.GeneratorProfitChart(StrategyName='RSI-long_short_cross')


#%%
###### (三) RSI 逆勢策略

OrderRecord = Record()
RSIPeriod = 5
Ceil = 80
Floor = 20
MoveStopLoss = 30
Order_Quantity = 3

KBar_dic['RSI'] = RSI(KBar_dic, timeperiod=RSIPeriod)
KBar_dic['Ceil'] = np.array([Ceil] * len(KBar_dic['time']))
KBar_dic['Floor'] = np.array([Floor] * len(KBar_dic['time']))

for n in range(1, len(KBar_dic['time']) - 1):
    if not np.isnan(KBar_dic['RSI'][n - 1]):
        if OrderRecord.GetOpenInterest() == 0:
            if KBar_dic['RSI'][n - 1] <= KBar_dic['Floor'][n - 1] and KBar_dic['RSI'][n] > KBar_dic['Floor'][n]:
                OrderRecord.Order('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice - MoveStopLoss
                continue

            if KBar_dic['RSI'][n - 1] >= KBar_dic['Ceil'][n - 1] and KBar_dic['RSI'][n] < KBar_dic['Ceil'][n]:
                OrderRecord.Order('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice + MoveStopLoss
                continue

        elif OrderRecord.GetOpenInterest() > 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Sell', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] - MoveStopLoss > StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] - MoveStopLoss
            elif KBar_dic['close'][n] < StopLossPoint:
                OrderRecord.Cover('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['RSI'][n] > KBar_dic['Ceil'][n]:
                OrderRecord.Cover('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], OrderRecord.GetOpenInterest())
                continue

        elif OrderRecord.GetOpenInterest() < 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Buy', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], -OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] + MoveStopLoss < StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] + MoveStopLoss
            elif KBar_dic['close'][n] > StopLossPoint:
                OrderRecord.Cover('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], -OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['RSI'][n] < KBar_dic['Floor'][n]:
                OrderRecord.Cover('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], -OrderRecord.GetOpenInterest())
                continue

# OrderRecord.GetTradeRecord()
# OrderRecord.GetProfit()
# OrderRecord.GetTotalProfit()
# OrderRecord.GetWinRate()
# OrderRecord.GetAccLoss()
# OrderRecord.GetMDD()
print('交易紀錄: \n', OrderRecord.GetTradeRecord())
print('\n')
print('利潤清單(TWD,點數): \n',OrderRecord.GetProfit())
print('\n')
print('淨利(TWD,點數): ',OrderRecord.GetTotalProfit())
print('\n')
print('勝率: ',OrderRecord.GetWinRate())
print('\n')
print('最大連續虧損(TWD,點數): ',OrderRecord.GetAccLoss())
print('\n')
print('最大累計盈虧(TWD,點數)回落: ',OrderRecord.GetMDD())
print('\n')
OrderRecord.GeneratorProfitChart(StrategyName='RSI_reversal')


#%%
###### (四) 布林通道策略

OrderRecord = Record()
BBANDSPeriod = 60
MoveStopLoss = 30
標準差倍數_上 = 2.0
標準差倍數_下 = 2.0
Order_Quantity = 1

KBar_dic['Upper'], KBar_dic['Middle'], KBar_dic['Lower'] = BBANDS(
    KBar_dic,
    timeperiod=BBANDSPeriod,
    nbdevup=標準差倍數_上,
    nbdevdn=標準差倍數_下,
    matype=0
)

for n in range(1, len(KBar_dic['time']) - 1):
    if not np.isnan(KBar_dic['Middle'][n - 1]):
        if OrderRecord.GetOpenInterest() == 0:
            if KBar_dic['close'][n - 1] <= KBar_dic['Lower'][n - 1] and KBar_dic['close'][n] > KBar_dic['Lower'][n]:
                OrderRecord.Order('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice - MoveStopLoss
                continue

            if KBar_dic['close'][n - 1] >= KBar_dic['Upper'][n - 1] and KBar_dic['close'][n] < KBar_dic['Upper'][n]:
                OrderRecord.Order('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], Order_Quantity)
                OrderPrice = KBar_dic['open'][n + 1]
                StopLossPoint = OrderPrice + MoveStopLoss
                continue

        elif OrderRecord.GetOpenInterest() > 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Sell', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] - MoveStopLoss > StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] - MoveStopLoss
            elif KBar_dic['close'][n] < StopLossPoint:
                OrderRecord.Cover('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] >= KBar_dic['Upper'][n]:
                OrderRecord.Cover('Sell', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], OrderRecord.GetOpenInterest())
                continue

        elif OrderRecord.GetOpenInterest() < 0:
            if KBar_dic['product'][n + 1] != KBar_dic['product'][n]:
                OrderRecord.Cover('Buy', KBar_dic['product'][n], KBar_dic['time'][n], KBar_dic['close'][n], -OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] + MoveStopLoss < StopLossPoint:
                StopLossPoint = KBar_dic['close'][n] + MoveStopLoss
            elif KBar_dic['close'][n] > StopLossPoint:
                OrderRecord.Cover('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], -OrderRecord.GetOpenInterest())
                continue

            if KBar_dic['close'][n] <= KBar_dic['Lower'][n]:
                OrderRecord.Cover('Buy', KBar_dic['product'][n + 1], KBar_dic['time'][n + 1], KBar_dic['open'][n + 1], -OrderRecord.GetOpenInterest())
                continue

# OrderRecord.GetTradeRecord()
# OrderRecord.GetProfit()
# OrderRecord.GetTotalProfit()
# OrderRecord.GetWinRate()
# OrderRecord.GetAccLoss()
# OrderRecord.GetMDD()
print('交易紀錄: \n', OrderRecord.GetTradeRecord())
print('\n')
print('利潤清單(TWD,點數): \n',OrderRecord.GetProfit())
print('\n')
print('淨利(TWD,點數): ',OrderRecord.GetTotalProfit())
print('\n')
print('勝率: ',OrderRecord.GetWinRate())
print('\n')
print('最大連續虧損(TWD,點數): ',OrderRecord.GetAccLoss())
print('\n')
print('最大累計盈虧(TWD,點數)回落: ',OrderRecord.GetMDD())
print('\n')
OrderRecord.GeneratorProfitChart(StrategyName='BBands Strategy')


#%%
###### (五) MACD 策略   
#%%
        if KBar_dic['close'][n] - MoveStopLoss > StopLossPoint:
            StopLossPoint = KBar_dic['close'][n] - MoveStopLoss


        # 停損出場
        elif KBar_dic['close'][n] < StopLossPoint:

            OrderRecord.Cover(
                'Sell',
                KBar_dic['product'][n+1],
                KBar_dic['time'][n+1],
                KBar_dic['open'][n+1],
                OrderRecord.GetOpenInterest()
            )
            continue


        # K跌破D
        elif K_now < D_now:

            OrderRecord.Cover(
                'Sell',
                KBar_dic['product'][n+1],
                KBar_dic['time'][n+1],
                KBar_dic['open'][n+1],
                OrderRecord.GetOpenInterest()
            )
            continue


    ################################################
    ###### 空單持有
    ################################################
    elif OrderRecord.GetOpenInterest() < 0:

        # 更新停損
        if KBar_dic['close'][n] + MoveStopLoss < StopLossPoint:
            StopLossPoint = KBar_dic['close'][n] + MoveStopLoss


        # 停損出場
        elif KBar_dic['close'][n] > StopLossPoint:

            OrderRecord.Cover(
                'Buy',
                KBar_dic['product'][n+1],
                KBar_dic['time'][n+1],
                KBar_dic['open'][n+1],
                -OrderRecord.GetOpenInterest()
            )
            continue


        # 黃金交叉回補
        elif K_now > D_now:

            OrderRecord.Cover(
                'Buy',
                KBar_dic['product'][n+1],
                KBar_dic['time'][n+1],
                KBar_dic['open'][n+1],
                -OrderRecord.GetOpenInterest()
            )
            continue


#%%
###### KDJ 績效輸出

print('====== KDJ Strategy ======')
print('交易紀錄:\n', OrderRecord.GetTradeRecord())
print('\n')
print('利潤清單:', OrderRecord.GetProfit())
print('淨利:', OrderRecord.GetTotalProfit())
print('勝率:', OrderRecord.GetWinRate())
print('最大連續虧損:', OrderRecord.GetAccLoss())
print('最大回落:', OrderRecord.GetMDD())

OrderRecord.GeneratorProfitChart(
    StrategyName='KDJ_Strategy'
)
