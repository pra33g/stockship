from ironCondor import IronCondor
from datetime import datetime, date, time, timedelta



##
stock = "NIFTY"
entry_day = None
entry_time = time(15, 14, 59)
exit_day = None
exit_time = time(15,14,59)


ic = IronCondor("NIFTY", "ic-backtest.csv", entry_day, entry_time , exit_day, exit_time)
ic.ironCondorAlgorithm()

####testing
# tt = time(0,0,1)
# for i in range(0, 5):
#     entry_time = datetime.combine(date.min, entry_time) - datetime.combine(date.min, tt)
#     entry_time = (datetime.min + entry_time).time()
#     print(type(entry_time))


