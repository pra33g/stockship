import pandas as pd
def getResults(df):
    ret = []
    for val in df['Sum']:
        if val is not None and not pd.isna(val):
            ret.append(val)
    return ret
def calc_totalProfit(results):
    ret = 0
    for val in results:
        if val > 0:
            ret += val
    return ret
def calc_totalLoss(results):
    ret = 0
    for val in results:
        if val < 0:
            ret += val
    return ret

def conWinLoss(results):
    retWin = []
    retLoss = []
    counterWin = 0
    counterLoss = 0
    for val in results:
        if val >= 0:
            counterWin += 1
            counterLoss = 0
        else:
            counterWin = 0
            counterLoss += 1
        retWin.append(counterWin)
        retLoss.append(counterLoss)
    return [retWin, retLoss]
def createSummary(data):
    df = pd.DataFrame(columns=[
        "results",
        "con.wins",
        "con.losses"
    ])
    df['results'] = getResults(data)
    results = df['results'].tolist()
    total_net = data['WeekCumulative'].tolist()[-1]
    total_profit = calc_totalProfit(results)
    total_loss = calc_totalLoss(results)
    [df["con.wins"],df["con.losses"]] = conWinLoss(results)
    max_con_wins = max(df['con.wins'])
    max_con_losses = max(df['con.losses'])

    print(f"total net:{total_net}\n"
    f"profit:{total_profit}\n"
    f"loss:{total_loss}\n"
    f"con_wins:{max_con_wins}\n"
    f"con_losses:{max_con_losses}")
    
