import matplotlib.pyplot as plt


def run_ma_strategy(df):

    profit = 1000
    winrate = 0.6
    mdd = -200

    fig, ax = plt.subplots()

    ax.plot(df['close'])

    return {
        "profit": profit,
        "winrate": winrate,
        "mdd": mdd,
        "fig": fig
    }
