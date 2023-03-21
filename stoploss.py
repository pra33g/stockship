from ironCondor import IronCondor
from  datetime import time
stock = "NIFTY"
entry_day = "THURSDAY"
entry_time = time(9, 29, 59)
exit_day = "THURSDAY"
exit_time = time(15,14,59)

ic = IronCondor(stock, "ic-backtest.csv", entry_day, entry_time , exit_day, exit_time)
ic.stoploss()
