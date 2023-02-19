from ironCondor import IronCondor
import datetime


##
stock = "NIFTY"
entry_day = "TUESDAY"
entry_time = datetime.time(15,14,59)
exit_day = "THURSDAY"
exit_time = datetime.time(15,14,59)


ic = IronCondor("NIFTY", "ic-backtest-tuethu.csv", entry_day, entry_time , exit_day, exit_time)
ic.ironCondorAlgorithm()
