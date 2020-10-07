import pandas as pd
import feather
from LC3377 import *


class DataFrame:
    def __init__(self, runNumber):
        self.name = "events_data_frame_" + str(runNumber)
        self.df0 = pd.DataFrame(columns=[
            'event_num', 'event_time', 'deadtime', 'TDC_L1_L', 'TDC_L1_R',
            'TDC_L2_L', 'TDC_L2_R', 'ADC', 'TDC', 'numChannelsRead', 'L1_asym',
            'L2_asym', 'L1_TDC_sum', 'L2_TDC_sum', 'L1_TDC_diff', 'L2_TDC_diff'
        ])
        self.eventNum = 0
        self.eventTime = 0
        self.deadTime = 0
        self.TDC_L1_L = 0
        self.TDC_L1_R = 0
        self.TDC_L2_L = 0
        self.TDC_L2_R = 0
        self.ADC = []
        self.TDC = []
        self.numChannelsRead = 0
        self.L1_asym = 0
        self.L2_asym = 0
        self.L1_TDC_sum = 0
        self.L2_TDC_sum = 0
        self.L1_TDC_diff = 0
        self.L2_TDC_diff = 0
        self.path = "processed_data/" + self.name + ".ftr"

    def updateDataFrame(self, info, eventNum):
        data_dict = self.getDataDict(info, eventNum)
        self.df0 = self.df0.append(data_dict, ignore_index=True)

    def getDataDict(self, info, eventNum):
        self.eventNum = eventNum
        self.eventTime = info.get('timeStamp')
        self.deadTime = info.get('deadtime')
        try:
            self.TDC_L1_L = info.get('unpacked3377Data').get((2, 0))
        except:
            self.TDC_L1_L = None
        try:
            self.TDC_L1_R = info.get('unpacked3377Data').get((2, 1))
        except:
            self.TDC_L1_R = None
        try:
            self.TDC_L2_L = info.get('unpacked3377Data').get((2, 3))
        except:
            self.TDC_L2_L = None
        try:
            self.TDC_L2_R = info.get('unpacked3377Data').get((2, 4))
        except:
            self.TDC_L2_R = None
        try:
            self.ADC = info.get((17, 'LeCroy2249'))
        except:
            self.ADC = None
        try:
            self.TDC = info.get("TDC").get("TDC")
            print(self.TDC)
        except:
            self.TDC = None
        try:
            self.numChannelsRead = info.get('len_unpacked_3377Data')
        except:
            self.numChannelsRead = None
        try:
            self.L1_asym = info.get('TDCAnalyzer').get('Layer1asym')
        except:
            self.L1_asym = None
        try:
            self.L2_asym = info.get('TDCAnalyzer').get('Layer2asym')
        except:
            self.L2_asym = None
        try:
            self.L1_TDC_sum = info.get('Layer_1').get('add_TDC')
        except:
            self.L1_TDC_sum = None
        try:
            self.L2_TDC_sum = info.get('Layer_2').get('add_TDC')
        except:
            self.L2_TDC_sum = None
        try:
            self.L1_TDC_diff = info.get('Layer_1').get('sub_TDC')
        except:
            self.L1_TDC_diff = None
        try:
            self.L2_TDC_diff = info.get('Layer_2').get('sub_TDC')
        except:
            self.L2_TDC_diff = None

        # xdefinitionL1, ydefinitionL1, xdefinitionL2, ydefinitionL2 = self.getLC3377Definition(
        # info)

        event_dict = {
            'event_num': self.eventNum,
            'event_time': self.eventTime,
            'deadtime': self.deadTime,
            'TDC_L1_L': self.TDC_L1_L,
            'TDC_L1_R': self.TDC_L1_R,
            'TDC_L2_L': self.TDC_L2_L,
            'TDC_L2_R': self.TDC_L2_R,
            'ADC': self.ADC,
            'TDC': self.TDC,
            'numChannelsRead': self.numChannelsRead,
            'L1_asym': self.L1_asym,
            'L2_asym': self.L2_asym,
            'L1_TDC_sum': self.L1_TDC_sum,
            'L2_TDC_sum': self.L2_TDC_sum,
            'L1_TDC_diff': self.L1_TDC_diff,
            'L2_TDC_diff': self.L2_TDC_diff
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
        self.df0.to_feather(self.path)
