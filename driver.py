from ironCondor import IronCondor
from datetime import datetime, date, time, timedelta
import summary


##
stock = "NIFTY"
entry_day = "FRIDAY"
entry_time = time(15, 14, 59)
exit_day = "THURSDAY"
exit_time = time(15,14,59)


ic = IronCondor("NIFTY", "ic-backtest.csv", entry_day, entry_time , exit_day, exit_time)
# [data, fname] = ic.ironCondorAlgorithm()
# print(data, fname)
# summary.createSummary(data, fname)

[data, fname] = ic.stoploss(-6000)
summary.createSummary(data, fname)
