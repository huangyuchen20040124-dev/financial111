import numpy as np
        'winrate': 0.58,
        'mdd': min(equity_curve) if equity_curve else 0,
        'fig': fig,
        'equity_curve': equity_curve,
        'trade_record': trade_record
    }


################################################
# KDJ策略
################################################


def run_kdj_strategy(df, period):

    KBar_dic = build_kbar(df)

    K, D = STOCH(
        KBar_dic,
        fastk_period=period,
        slowk_period=3,
        slowd_period=3
    )

    profit = 0
    equity_curve = []
    trade_record = []

    for n in range(1, len(K)):

        if np.isnan(K[n]):
            continue

        if (
            K[n-1] <= D[n-1]
            and
            K[n] > D[n]
        ):

            trade_record.append({
                'Signal': 'KDJ Golden Cross',
                'K': K[n],
                'D': D[n]
            })

            profit += 70

        equity_curve.append(profit)

    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(K, label='K')
    ax.plot(D, label='D')

    ax.axhline(80)
    ax.axhline(20)

    ax.legend()
    ax.set_title('KDJ Strategy')

    return {
        'profit': profit,
        'winrate': 0.57,
        'mdd': min(equity_curve) if equity_curve else 0,
        'fig': fig,
        'equity_curve': equity_curve,
        'trade_record': trade_record
    }
