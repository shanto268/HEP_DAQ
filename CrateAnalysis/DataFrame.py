import pandas as pd
# import modin.pandas as pd
import feather
from LC3377 import *


class DataFrame:
    def __init__(self, runNumber):
        self.name = "events_data_frame_" + str(runNumber)
        # self.df0 = pd.DataFrame(
        # columns=['event_num', 'event_time', 'deadtime'])
        self.df0 = pd.DataFrame(columns=[
            'event_num', 'event_time', 'deadtime', 'ADC', 'TDC', 'Scaler'
        ])
        self.eventNum = 0
        self.eventTime = 0
        self.deadTime = 0
        self.ADC = []
        self.TDC = []
        self.Scaler = []
        self.data_dict = []
        self.path = "processed_data/" + self.name + ".ftr"

    def updateDataFrame(self, info, eventNum):
        self.data_dict.append(self.getDataDict(info, eventNum))
        # self.df0 = self.df0.append(data_dict, ignore_index=True)

    def getDataDict(self, info, eventNum):
        self.eventNum = eventNum
        self.eventTime = info.get('timeStamp')
        self.deadTime = info.get('deadtime')
        try:
            self.ADC = info.get((17, 'LeCroy2249'))
        except:
            self.ADC = None
        try:
            self.TDC = info.get("TDC").get("TDC")
        except:
            self.TDC = None
        try:
            self.Scaler = info.get((5, 'LeCroy2552'))
        except:
            self.Scaler = None

        event_dict = {
            'event_num': self.eventNum,
            'event_time': self.eventTime,
            'deadtime': self.deadTime,
            'ADC': self.ADC,
            'TDC': self.TDC,
            'Scaler': self.Scaler
        }
        return event_dict

    def showDataFrame(self):
        print(self.df0)
        # pass

    def getLC3377Definition(self, info):
        pass

    def LC3377Definition(self, slot, channel, info, invalidtdc):
        pass

    def trial(self, info):
        self.deadTime = info.get('deadtime')
        return {'deadTime': self.deadTime}

    def saveDataFrame(self):
        print("Saving the DataFrame....")
        self.df0 = pd.DataFrame.from_dict(self.data_dict)
        feather.write_dataframe(self.df0, self.path)
        # self.df0.to_feather(self.path)
