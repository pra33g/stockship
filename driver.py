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
[data, fname] = ic.ironCondorAlgorithm()
summary.createSummary(data, fname)
####testing
# tt = time(0,0,1)
# for i in range(0, 5):
#     entry_time = datetime.combine(date.min, entry_time) - datetime.combine(date.min, tt)
#     entry_time = (datetime.min + entry_time).time()
#     print(type(entry_time))


