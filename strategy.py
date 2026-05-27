import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from talib.abstract import SMA
from talib.abstract import RSI
from talib.abstract import MACD
from talib.abstract import STOCH

from order_Lo8 import Record


################################################
# 共用KBar格式
################################################

def build_kbar(df):

    KBar_dic = {}

    KBar_dic['open'] = np.array(df['open']).astype(float)
    KBar_dic['high'] = np.array(df['high']).astype(float)
    KBar_dic['low'] = np.array(df['low']).astype(float)
    KBar_dic['close'] = np.array(df['close']).astype(float)
    KBar_dic['volume'] = np.array(df['volume'])

    KBar_dic['time'] = np.array(
        pd.to_datetime(df['time'])
    )

    KBar_dic['product'] = np.repeat(
        'tsmc',
        len(df)
    )

    return KBar_dic


################################################
# MA策略
################################################

def run_ma_strategy(df):

    KBar_dic = build_kbar(df)

    OrderRecord = Record()

    KBar_dic['MA_long'] = SMA(
        KBar_dic,
        timeperiod=20
    )

    KBar_dic['MA_short'] = SMA(
        KBar_dic,
        timeperiod=5
    )

    for n in range(1, len(KBar_dic['time']) - 1):

        if np.isnan(KBar_dic['MA_long'][n]):
            continue

        if OrderRecord.GetOpenInterest() == 0:

            if (
                KBar_dic['MA_short'][n-1]
                <=
                KBar_dic['MA_long'][n-1]
            ) and (
                KBar_dic['MA_short'][n]
                >
                KBar_dic['MA_long'][n]
            ):

                OrderRecord.Order(
                    'Buy',
                    KBar_dic['product'][n+1],
                    KBar_dic['time'][n+1],
                    KBar_dic['open'][n+1],
                    1
                )

    fig, ax = plt.subplots()

    ax.plot(KBar_dic['close'])
    ax.plot(KBar_dic['MA_long'])
    ax.plot(KBar_dic['MA_short'])

    ax.set_title("MA Strategy")

    return {
        "profit": OrderRecord.GetTotalProfit(),
        "winrate": OrderRecord.GetWinRate(),
        "mdd": OrderRecord.GetMDD(),
        "fig": fig
    }


################################################
# RSI策略
################################################

def run_rsi_strategy(df):

    KBar_dic = build_kbar(df)

    OrderRecord = Record()

    KBar_dic['RSI'] = RSI(
        KBar_dic,
        timeperiod=14
    )

    for n in range(1, len(KBar_dic['time']) - 1):

        if np.isnan(KBar_dic['RSI'][n]):
            continue

        if OrderRecord.GetOpenInterest() == 0:

            if KBar_dic['RSI'][n] < 30:

                OrderRecord.Order(
                    'Buy',
                    KBar_dic['product'][n+1],
                    KBar_dic['time'][n+1],
                    KBar_dic['open'][n+1],
                    1
                )

    fig, ax = plt.subplots()

    ax.plot(KBar_dic['RSI'])

    ax.axhline(70)
    ax.axhline(30)

    ax.set_title("RSI Strategy")

    return {
        "profit": OrderRecord.GetTotalProfit(),
        "winrate": OrderRecord.GetWinRate(),
        "mdd": OrderRecord.GetMDD(),
        "fig": fig
    }


################################################
# MACD策略
################################################

def run_macd_strategy(df):

    KBar_dic = build_kbar(df)

    OrderRecord = Record()

    macd, signal, hist = MACD(
        KBar_dic,
        fastperiod=12,
        slowperiod=26,
        signalperiod=9
    )

    KBar_dic['MACD'] = macd
    KBar_dic['Signal'] = signal

    for n in range(1, len(KBar_dic['time']) - 1):

        if np.isnan(KBar_dic['MACD'][n]):
            continue

        if OrderRecord.GetOpenInterest() == 0:

            if (
                KBar_dic['MACD'][n-1]
                <=
                KBar_dic['Signal'][n-1]
            ) and (
                KBar_dic['MACD'][n]
                >
                KBar_dic['Signal'][n]
            ):

                OrderRecord.Order(
                    'Buy',
                    KBar_dic['product'][n+1],
                    KBar_dic['time'][n+1],
                    KBar_dic['open'][n+1],
                    1
                )

    fig, ax = plt.subplots()

    ax.plot(KBar_dic['MACD'])
    ax.plot(KBar_dic['Signal'])

    ax.set_title("MACD Strategy")

    return {
        "profit": OrderRecord.GetTotalProfit(),
        "winrate": OrderRecord.GetWinRate(),
        "mdd": OrderRecord.GetMDD(),
        "fig": fig
    }


################################################
# KDJ策略
################################################

def run_kdj_strategy(df):

    KBar_dic = build_kbar(df)

    OrderRecord = Record()

    K, D = STOCH(
        KBar_dic,
        fastk_period=9,
        slowk_period=3,
        slowd_period=3
    )

    KBar_dic['K'] = K
    KBar_dic['D'] = D

    for n in range(1, len(KBar_dic['time']) - 1):

        if np.isnan(KBar_dic['K'][n]):
            continue

        if OrderRecord.GetOpenInterest() == 0:

            if (
                KBar_dic['K'][n-1]
                <=
                KBar_dic['D'][n-1]
            ) and (
                KBar_dic['K'][n]
                >
                KBar_dic['D'][n]
            ):

                OrderRecord.Order(
                    'Buy',
                    KBar_dic['product'][n+1],
                    KBar_dic['time'][n+1],
                    KBar_dic['open'][n+1],
                    1
                )

    fig, ax = plt.subplots()

    ax.plot(KBar_dic['K'])
    ax.plot(KBar_dic['D'])

    ax.axhline(80)
    ax.axhline(20)

    ax.set_title("KDJ Strategy")

    return {
        "profit": OrderRecord.GetTotalProfit(),
        "winrate": OrderRecord.GetWinRate(),
        "mdd": OrderRecord.GetMDD(),
        "fig": fig
    }
