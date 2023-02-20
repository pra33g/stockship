from ironCondor import IronCondor
import datetime


##
stock = "NIFTY"
entry_day = None
entry_time = datetime.time(15,14,59)
exit_day = None
exit_time = datetime.time(15,14,59)


ic = IronCondor("NIFTY", "ic-backtest", entry_day, entry_time , exit_day, exit_time)
ic.ironCondorAlgorithm()
