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
        if val > 0:
            counterWin += 1
            counterLoss = 0
        elif val < 0:
            counterWin = 0
            counterLoss += 1
        retWin.append(counterWin)
        retLoss.append(counterLoss)
    return [retWin, retLoss]

def calcAvgWins(results, total):
    counter = 0
    for val in results:
        if val > 0:
            counter += 1
    return total / counter
def calcAvgLosses(results, total):
    counter = 0
    for val in results:
        if val < 0:
            counter += 1
    return total / counter

def minDrawdown(data):
    ret = 0
    for val in data:
        if not pd.isna(val) and val < ret:
            ret = val
    return ret
def createSummary(data, fname):
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
    lots = 2
    margin = 50000
    final_drawDown = abs(minDrawdown(data['Drawdown']) * lots)
    total_return = data['WeekCumulative'].tolist()[-1] * lots
    calmar = (total_return / final_drawDown)
    avg_win = calcAvgWins(df['results'], total_profit)
    avg_loss = calcAvgLosses(df['results'], total_loss)
    rr = avg_win / avg_loss
    total_trades = int(4 * lots * (len(data) / 4))
    brokerage = total_trades * 20
    brokerage_margin = margin * lots
    brokerage_cost = brokerage / brokerage_margin 
    slippage = 5 / 100
    slippage_margin = brokerage_margin
    slippage_cost = slippage_margin * slippage
    tax = sum(data['TotalCost'])
    tax_cost = (tax*lots / (margin * lots))

    drawdown_percentage = final_drawDown / brokerage_margin * 100
    totalreturn_percentage = total_return / brokerage_margin * 100

    actual_dd = drawdown_percentage + (brokerage_cost * 100) + (slippage * 100) + (tax_cost * 100)

    actual_roi = totalreturn_percentage - (brokerage_cost * 100) - (slippage * 100) - (tax_cost * 100)


    
    print(actual_dd, actual_roi)
    print(actual_roi / actual_dd)

    app = pd.DataFrame(columns=[
        "bt",
        "dd",
        "roi",
        "roi/dd"
    ])
    app.loc[len(app)] = [fname, actual_dd, actual_roi, (actual_roi/actual_dd)]
    #write data to file
    #results.csv must exist
    #read df
    df = pd.read_csv("results.csv")
    final_df = pd.concat([df, app], ignore_index=True)
    final_df.to_csv("results.csv", index=False)
    # print(f"total net:{total_net}\n"
    # f"profit:{total_profit}\n"
    # f"loss:{total_loss}\n"
    # f"con_wins:{max_con_wins}\n"
    # f"con_losses:{max_con_losses}")
    
