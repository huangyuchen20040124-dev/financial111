import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from talib.abstract import SMA
from talib.abstract import RSI
from talib.abstract import MACD
from talib.abstract import STOCH


################################################
# 建立KBar格式
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

    return KBar_dic


################################################
# MA策略
################################################


def run_ma_strategy(df, short_period, long_period):

    KBar_dic = build_kbar(df)

    short_ma = SMA(
        KBar_dic,
        timeperiod=short_period
    )

    long_ma = SMA(
        KBar_dic,
        timeperiod=long_period
    )

    profit = 0
    equity_curve = []
    trade_record = []

    for n in range(1, len(KBar_dic['close'])):

        if np.isnan(short_ma[n]):
            continue

        if (
            short_ma[n-1] <= long_ma[n-1]
            and
    }
