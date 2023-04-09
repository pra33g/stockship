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
stopLoss = None

if __name__ == "__main__":
    args = sys.argv[1:]
    entry_day = args[0]
    entry_time = time(int(args[1]), int(args[2]), int(args[3]))
    exit_day = args[4]
    exit_time = time(int(args[5]), int(args[6]), int(args[7]))
    if len(args) == 9:
        stopLoss = int(args[8])
    # print(args)
    # print(entry_day, exit_day, entry_time, exit_time, sep="\n")
    ic = IronCondor("NIFTY", entry_day, entry_time , exit_day, exit_time)
    data = None
    fname = None
    if stopLoss is not None:
        [data, fname] = ic.stoploss(stoploss=stopLoss)
    else:
        [data, fname] = ic.ironCondorAlgorithm()

summary.createSummary(data, fname)

# ic = IronCondor("NIFTY", entry_day, entry_time , exit_day, exit_time)
# [data, fname] = ic.stoploss(stoploss=stopLoss)
# summary.createSummary(data, fname)
 