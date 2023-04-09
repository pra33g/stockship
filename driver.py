from ironCondor import IronCondor
from datetime import datetime, date, time, timedelta
import summary
import sys

##
stock = "NIFTY"
entry_day = "FRIDAY"
entry_time = time(15, 14, 59)
exit_day = "THURSDAY"
exit_time = time(15,14,59)
stopLoss = -2000

# if __name__ == "__main__":
#     args = sys.argv[1:]
#     print(args)
# ic = IronCondor("NIFTY", entry_day, entry_time , exit_day, exit_time)
# data = None
# fname = None
# if stopLoss is not None:
#     [data, fname] = ic.stoploss(stoploss=stopLoss)
# else:
#     [data, fname] = ic.ironCondorAlgorithm()

# summary.createSummary(data, fname)
ic = IronCondor("NIFTY", entry_day, entry_time , exit_day, exit_time)
[data, fname] = ic.stoploss(stoploss=stopLoss)
summary.createSummary(data, fname)
 