# -*- coding: utf-8 -*-
    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(KBar_dic['RSI'])
    ax.set_title('RSI Strategy')

    return {
        'profit': OrderRecord.GetTotalProfit(),
        'winrate': OrderRecord.GetWinRate(),
        'mdd': OrderRecord.GetMDD(),
        'fig': fig
    }


################################################
# 布林通道策略
################################################

def run_bbands_strategy(df):

    KBar_dic = build_kbar_dict(df)

    upper, middle, lower = BBANDS(
        KBar_dic,
        timeperiod=20,
        nbdevup=2,
        nbdevdn=2
    )

    KBar_dic['Upper'] = upper
    KBar_dic['Middle'] = middle
    KBar_dic['Lower'] = lower

    OrderRecord = Record()

    for n in range(1, len(KBar_dic['time']) - 1):

        if np.isnan(KBar_dic['Middle'][n]):
            continue

        if OrderRecord.GetOpenInterest() == 0:

            if KBar_dic['close'][n] < KBar_dic['Lower'][n]:

                OrderRecord.Order(
                    'Buy',
                    KBar_dic['product'][n+1],
                    KBar_dic['time'][n+1],
                    KBar_dic['open'][n+1],
                    1
                )

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(KBar_dic['close'], label='Close')
    ax.plot(KBar_dic['Upper'], label='Upper')
    ax.plot(KBar_dic['Middle'], label='Middle')
    ax.plot(KBar_dic['Lower'], label='Lower')

    ax.legend()
    ax.set_title('BBANDS Strategy')

    return {
        'profit': OrderRecord.GetTotalProfit(),
        'winrate': OrderRecord.GetWinRate(),
        'mdd': OrderRecord.GetMDD(),
        'fig': fig
    }
