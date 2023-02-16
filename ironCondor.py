import weeklyData
import pandas as pd
import datetime
import helper
import os
class IronCondor:
    defaultExitTime = datetime.time(15, 14, 59)
    defaultEntryTime = datetime.time(15, 14, 59)
    def __init__(self, stockName, entryDay = None, entryTime = None, exitDay = None, exitTime = None):
        self.stockName = stockName
        self.entryDay = entryDay
        self.entryTime = entryTime
        self.exitDay = exitDay
        self.exitTime = exitTime

    def calcEntryDate(self, week, prefDay):
        ret = None
        if prefDay is None:
            ret = week[0]
        else:
            wdli = helper.weekDaysList.index
            prefDayIndex = wdli(prefDay)
            for day in week:
                curDay = day['Day']
                curDayIndex = wdli(curDay)
                if curDayIndex >= prefDayIndex:
                    ret = day
                    break
        return ret.Date
    def calcExitDate(self, week, prefDay):
        ret = None
        if prefDay is None:
            ret = week[-1]
        else:
            wdli = helper.weekDaysList.index
            prefDayIndex = wdli(prefDay)
            for day in week:
                curDay = day['Day']
                curDayIndex = wdli(curDay)
                if curDayIndex <= prefDayIndex:
                    ret = day
            if ret is None:
                ret = week[0]
        return ret.Date
    def calcEntryTime(self):
        if self.entryTime is None:
            self.entryTime = IronCondor.defaultEntryTime
        return self.entryTime

    def calcExitTime(self):
        if self.exitTime is None:
            self.exitTime = IronCondor.defaultExitTime
        return self.exitTime

    def loadPrices(self, dates, strikePrices):
        symbol = "NFO"
        extension = "csv"
        fileNamePrefix = "GFDL"
        data_dir = f"{self.stockName}_OPTIONS_DATA"

        for date in dates:       
            #NIFTY03FEB22171800PE.NFO
            day = "{:02d}".format(date.day)
            yearStripped = str(date.year)[-2:]
            month = helper.Month[date.month - 1]
            month_num = "{:02d}".format(date.month)
            month_dir = f"{month}_{date.year}"
            fileName = f"{fileNamePrefix}{symbol}_OPTIONS_{day}{month_num}{date.year}.{extension}"
            filePath = os.path.join(data_dir, month_dir, fileName)
            df = pd.read_csv(filePath)
            #df[(df[""])]
            for idx, strikePrice in enumerate(strikePrices):
                optionType = None
                if idx % 2 == 0:
                    optionType = "CE"
                else:
                    optionType = "PE"
                stock_id = f"{self.stockName}{day}{month}{yearStripped}{strikePrice}{optionType}.{symbol}"
                print(stock_id)
    def ironCondorAlgorithm(self):
        weeklyData_tup = weeklyData.createWeeklyData(self.stockName)
        wd = weeklyData_tup[0]
        weeks = weeklyData_tup[1]

        df = pd.DataFrame(columns=[
            "OptionType", 
            "WeekBeginDate", #
            "WeekExpiry",# 
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
            "Cumulative",
        ])
        for idx, data in wd.iterrows():
            weekBegin = weeks[idx][0]['Date']
            weekExpiry = weeks[idx][-1]['Date']
            #set entry date
            entryDate = self.calcEntryDate(weeks[idx], self.entryDay)
            #set exit date
            exitDate = self.calcExitDate(weeks[idx], self.exitDay)
            entryTime = self.calcEntryTime()
            exitTime = self.calcExitTime()
            #load strike prices
            ce1 = data['CE1']
            pe1 = data['PE1']
            ce2 = data['CE2']
            pe2 = data['PE2']
            self.loadPrices([entryDate, exitDate], [ce1, pe1, ce2, pe2])
            #get entry prices based on stockname, date, optiontype
            input()
ic = IronCondor("NIFTY", "WEDNESDAY", datetime.time(0,0,0), "THURSDAY", datetime.time(0,0,0,0))
ic.ironCondorAlgorithm()
