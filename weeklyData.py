import helper
import pandas as pd

def createWeeklyData(stock):
    df = pd.read_csv(f"{stock}.csv")

    days = df['Day']
    weekDays = [
        "Friday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
    ]
    idx_weeks = 0
    weeks = [[]]
    for idx_days, day in enumerate(days):
        if pd.isna(day):
            continue
        # weeks[idx_weeks].append(df.loc[idx_days].values.tolist())
        weeks[idx_weeks].append(df.loc[idx_days])
        if not pd.isna(days[idx_days + 1]) and weekDays.index(days[idx_days]) >= weekDays.index(days[idx_days + 1]):
            idx_weeks += 1
            weeks.append([])

    week_df = pd.DataFrame(columns = [
        "Date",
        "Day",
        "WeekOpen",
        "WeekHigh",
        "WeekLow",
        "WeekClose",
        "High-Low",
    ])

    for i, week in enumerate(weeks):
        w_high = week[0]["High"]
        w_low = week[0]["Low"]
        w_open = week[0]["Open"]
        #set close to next week's first day's close
        if i == len(weeks) - 1:
            #set to current week's last day's close
            w_close = weeks[i][-1]["Close"]
        else:
            #set to next week's first day's close
            w_close = weeks[i + 1][0]["Close"]
        w_date = week[-1]["Date"]
        w_day = week[-1]["Day"]
        for day in week:
            if day["High"] > w_high:
                w_high = day["High"]
            if day["Low"] < w_low:
                w_low = day["Low"]    
        # print(w_date, w_day, w_high, w_low, w_close, i)
        week_df.loc[len(week_df)] = [
            w_date,
            w_day,
            w_open,
            w_high,
            w_low,
            w_close,
            w_high - w_low
        ]

    year_hl_mean = week_df['High-Low'].mean()
    year_hl_median = week_df['High-Low'].median()

    ce1Temp = []
    pe1Temp = []
    ce2Temp = []
    pe2Temp = []
    roundBase = 50
    for i,val in enumerate(week_df['WeekClose']):
        constant = year_hl_mean / 2
        #round the constant to nearest roundbase
        constant = helper.roundDown(constant, roundBase)
        #set ce,pe and round it
        ce1 = val + constant
        pe1 = val - constant
        ce2 = ce1 + constant
        pe2 = pe1 - constant
        ce1 = helper.roundDown(ce1, roundBase)
        ce2 = helper.roundDown(ce2, roundBase)
        pe1 = helper.roundDown(pe1, roundBase)
        pe2 = helper.roundDown(pe2, roundBase)
        #add ce, pe to lists
        ce1Temp.append(ce1)
        pe1Temp.append(pe1)
        ce2Temp.append(ce2)
        pe2Temp.append(pe2)

    week_df['CE1'] = ce1Temp
    week_df['PE1'] = pe1Temp
    week_df['CE2'] = ce2Temp
    week_df['PE2'] = pe2Temp
    return week_df