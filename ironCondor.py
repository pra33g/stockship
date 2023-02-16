import weeklyData
import pandas as pd
import datetime
import helper
class IronCondor:
    def __init__(self, stockName, entryDay, entryTime, exitDay, exitTime):
        self.stockName = stockName
        self.entryDay = entryDay
        self.entryTime = entryTime
        self.exitDay = exitDay
        self.exitTime = exitTime
        
    def loadPrice(self, stock, date, optionType, entryTime, exitTime):
        symbol = "NFO"
        data_dir = f"{stock}_OPTIONS_DATA"
        month_dir = f"{helper.Month[date.month - 1]}_{date.year}"
        #stock_id =
 
    def ironCondorAlgorithm(self):
        weeklyData_tup = weeklyData.createWeeklyData(self.stockName)
        wd = weeklyData_tup[0]
        weeks = weeklyData_tup[1]

        df = pd.DataFrame(columns=[
            "OptionType", 
            "Date", #
            "Expiry",# 
            "EntryDate", #
            "EntryTime",#
            "ExitDate", #
            "ExitTime",#
            "StrikePrice",
            "EntryPrice",
            "Spread", #
            "ExitPrice", 
            "Profit", #
            "Sum", #
            "Cumulative"
        ])
        for idx, data in wd.iterrows():
            #set entry date
            entryDate = self.setEntryDate(weeks[idx], self.entryDay)
       
            #set exit date
            exitDate = self.setExitDate(weeks[idx], self.exitDay)
            break
            # stocks = []
            # ce1 = data['CE1']
            # pe1 = data['PE1']
            # ce2 = data['CE2']
            # pe2 = data['PE2']
            # get entry prices based on stockname, date, optiontype
            break

ic = IronCondor("NIFTY", "FRIDAY", datetime.time(0,0,0), "WEDNESDAY", datetime.time(0,0,0,0))
ic.ironCondorAlgorithm()
