import weeklyData
import pandas as pd
import datetime
import helper
import os
import traceback
from collections import namedtuple
from enum import IntEnum
class OptionsEnum(IntEnum):
    CE1 = 0
    PE1 = 1
    CE2 = 2
    PE2 = 3
class IronCondor:
    oe = OptionsEnum
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
        return ret.Date.date()
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
        return ret.Date.date()
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
        #day, yearstripped, year, month, monthnum, year
        dateDataTuple = namedtuple("dateDataTuple", ["day", "year", "yearStripped", "month", "monthNum"])
        class dateIdEnum(IntEnum):
            ENTRY = 0
            EXIT = 1
        dateData = []
        for d in dates:
            dateData.append(
                dateDataTuple(
                    "{:02d}".format(d.day),
                    d.year,
                    str(d.year)[-2:],
                    helper.Month[d.month - 1],
                    "{:02d}".format(d.month)
                )
            )
        ##generate tickers
        tickers = []
        date = dateData[dateIdEnum.EXIT] #dateData[1] is the exitDay
#        for date in dates:
            #NIFTY03FEB22171800PE.NFO
        for idx, strikePrice in enumerate(strikePrices):
            optionType = None
            if idx % 2 == 0:
                optionType = "CE"
            else:
                optionType = "PE"
            stock_id = f"{self.stockName}{date.day}{date.month}{date.yearStripped}{strikePrice}{optionType}.{symbol}"
            tickers.append(stock_id)

        ##get data from files
        extension = "csv"
        fileNamePrefix = "GFDL"
        data_dir = f"{self.stockName}_OPTIONS_DATA"
        entryPrices = []
        exitPrices = []
        for i, dd in enumerate(dateData):
            month_dir = f"{dd.month}_{dd.year}"
            fileName = f"{fileNamePrefix}{symbol}_OPTIONS_{dd.day}{dd.monthNum}{dd.year}.{extension}"
            filePath = os.path.join(data_dir, month_dir, fileName)
            df = pd.read_csv(filePath)
            Time = None
            try:
                debugInfo = [None, None, None]
                if i == dateIdEnum.ENTRY:
                    debugInfo[0] = "Entry"
                    Time = self.entryTime
                    debugInfo[1] = Time
                    for ticker in tickers:
                        entryPrices.append(df[(df["Ticker"] == ticker) & (df["Time"] == str(Time))]['Close'].values[0])
                        debugInfo[2] = ticker
                elif i == dateIdEnum.EXIT:
                    debugInfo[0] = "Exit"
                    Time = self.exitTime
                    debugInfo[1] = Time

                    for ticker in tickers:
                        exitPrices.append(df[(df["Ticker"] == ticker) & (df["Time"] == str(Time))]['Close'].values[0])
                        debugInfo[2] = ticker

            except Exception as e:
                #traceback.print_exc()
                print("Error:",[i, debugInfo, filePath])
            
        return [entryPrices, exitPrices, tickers]
    def calcSpread(entryPrices):
            oe = IronCondor.oe
            return (
                entryPrices[oe.CE1]
                +entryPrices[oe.PE1]
                -(
                    entryPrices[oe.CE2]
                    +entryPrices[oe.PE2]
                )
            )
    def ironCondorAlgorithm(self):
        weeklyData_tup = weeklyData.createWeeklyData(self.stockName)
        wd = weeklyData_tup[0]
        weeks = weeklyData_tup[1]
        df = pd.DataFrame(columns=[
            "WeekBeginDate", #
            "WeekBeginDay",#
            "WeekExpiryDate",#
            "WeekExpiryDay",#
            "EntryDate", #
            "EntryDay",#
            "EntryTime",#
            "ExitDate", #
            "ExitDay",#
            "ExitTime",#
            "Ticker",
            "EntryPrice",
            "Spread", #
            "ExitPrice", 
            "Profit", #
            "Sum", #
            "Cumulative",
        ])

        for idx, data in wd.iterrows():
            print(idx)
            weekBegin = weeks[idx][0]['Date'].date()
            weekExpiry = weeks[idx][-1]['Date'].date()
            #set entry date
            entryDate = self.calcEntryDate(weeks[idx], self.entryDay)
            #set exit date
            exitDate = self.calcExitDate(weeks[idx], self.exitDay)
            entryTime = self.calcEntryTime()
            exitTime = self.calcExitTime()
            #load strike prices

            optionStrikePrices = [
                data['CE1'],
                data['PE1'],
                data['CE2'],
                data['PE2'],
            ]
            #get prices based on stockname, date, optiontype
            [entryPrices, exitPrices, tickers] = self.loadPrices([entryDate, exitDate], optionStrikePrices)
            #calculate spread
            spread = IronCondor.calcSpread(entryPrices)
            oe = IronCondor.oe
            cumulative = 0
            try:
                #add first row of four
                data = [
                    weekBegin,
                    wd.loc[idx]['FirstDay'],
                    weekExpiry,
                    wd.loc[idx]['LastDay'],
                    entryDate,
                    helper.weekDaysListNormal[entryDate.weekday()],
                    self.entryTime,
                    exitDate,
                    helper.weekDaysListNormal[exitDate.weekday()],
                    self.exitTime,
                    tickers[oe.CE1],
                    entryPrices[oe.CE1],
                    None,
                    exitPrices[oe.CE1],
                    None, None, None,
                ]
                df.loc[len(df)] = data
                #second row
                data = [
                    None, None, None, None, None, None, None, None, None, None,
                    tickers[oe.PE1],
                    entryPrices[oe.PE1],
                    None,
                    exitPrices[oe.PE1],
                    None, None, None,
                ]
                df.loc[len(df)] = data
                #third row
                data = [
                    None, None, None, None, None, None, None, None, None, None,
                    tickers[oe.CE2],
                    entryPrices[oe.CE2],
                    None,
                    exitPrices[oe.CE2],
                    None, None, None,
                ]
                df.loc[len(df)] = data
                #fourth row
                data = [
                    None, None, None, None, None, None, None, None, None, None,
                    tickers[oe.PE2],
                    entryPrices[oe.PE2],
                    None,
                    exitPrices[oe.PE2],
                    None, None, None,
                ]
                df.loc[len(df)] = data
            except Exception as e:
                print(e)
                print("Error: ", idx)
            
        df.to_csv("ironCondorAlgo.csv", index=False)
ic = IronCondor("NIFTY", None, None, None, None)
ic.ironCondorAlgorithm()
