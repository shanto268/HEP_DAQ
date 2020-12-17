import matplotlib.pyplot as plt
import numpy as np

from UtilityModules import DummyModule
from collections import Counter


class MissingTDCCounter(DummyModule):
    # In the constructor, provide whatever arguments
    # you intend to play with
    def __init__(self, name):
        DummyModule.__init__(self, name)
        self.l1 = []
        self.l2 = []
        self.l3 = []
        self.l4 = []
        self.r1 = []
        self.r2 = []
        self.r3 = []
        self.r4 = []
        self.total = 0

    def printSpecificData(self, item, eventNumber, eventRecord):
        print(eventNumber,
              "Key : {} , Value : {}".format(item, eventRecord[item]))
        #print(eventNumber,"Value : {}, Len: {}".format(eventRecord.get(item), len(eventRecord.get(item))))

    def printRawDataOutput(self, eventNumber, eventRecord):
        for item in eventRecord:
            #print(item)
            print(eventNumber,
                  "Key : {} , Value : {}".format(item, eventRecord[item]))

    def processEvent(self, runNumber, eventNumber, eventRecord):
        # self.printRawDataOutput(eventNumber, eventRecord)
        # self.printSpecificData("TDC", eventNumber, eventRecord)
        tdc = eventRecord["TDC"].get("TDC")
        # print(tdc)
        if tdc != None:
            channels = [i[0] for i in tdc]
            # 1 is there, 0 is bad
            if 0 in channels:
                self.l1.append(1)
            else:
                self.l1.append(0)

            if 1 in channels:
                self.r1.append(1)
            else:
                self.r1.append(0)

            if 2 in channels:
                self.l2.append(1)
            else:
                self.l2.append(0)

            if 3 in channels:
                self.r2.append(1)
            else:
                self.r2.append(0)

            if 6 in channels:
                self.l3.append(1)
            else:
                self.l3.append(0)

            if 7 in channels:
                self.r3.append(1)
            else:
                self.r3.append(0)

            if 8 in channels:
                self.l4.append(1)
            else:
                self.l4.append(0)

            if 9 in channels:
                # print(channels)
                self.r4.append(1)
            else:
                self.r4.append(0)
        else:
            pass

    def endRun(self, runNumber, runRecord):
        self.total = (len(runRecord) - 9) / 100

    def beginRun(self, runNumber, runRecord):
        self.total = (len(runRecord) - 9) / 100

    def endJob(self):
        """Plot Graph Here:
            divide each value by self.total
        """
        l1_p = self.l1.count(1)
        # print("l1_p : {}".format(l1_p))
        l2_p = self.l2.count(1)
        # print("l2_p: ", l2_p)
        l3_p = self.l3.count(1)
        # print("l3_p: ", l3_p)
        l4_p = self.l4.count(1)
        # print("l4_p : ", l4_p)
        r1_p = self.r1.count(1)
        # print("r1_p : ", r1_p)
        r2_p = self.r2.count(1)
        # print("r2_p : ", r2_p)
        r3_p = self.r3.count(1)
        # print("r3_p : ", r3_p)
        r4_p = self.r4.count(1)
        # print("r4_p : ", r4_p)

        yvals = [
            l1_p / self.total, r1_p / self.total, l2_p / self.total,
            r2_p / self.total, l3_p / self.total, r3_p / self.total,
            l4_p / self.total, r4_p / self.total
        ]

        xvals = [
            "Ch 0", "Ch 1", "Ch 2", "Ch 3", "Ch 6", "Ch 7", "Ch 8", "Ch 9"
        ]
        barlist = plt.bar(xvals, yvals)
        barlist[0].set_color('r')
        barlist[1].set_color('r')
        barlist[4].set_color('r')
        barlist[5].set_color('r')
        plt.title("Percentage of Good Events")
        plt.show()

    def endJob_og(self):
        """Plot Graph Here:
            divide each value by self.total
        """
        l1_p = list(Counter(
            self.l1).values())  # counts the elements' frequency
        print("l1_p : {}".format(l1_p))
        l1_p = (l1_p[1] * 100 / self.total)
        l2_p = list(Counter(
            self.l2).values())  # counts the elements' frequency
        print("l2_p: {}", l2_p)
        l2_p = (l2_p[1] * 100 / self.total)
        l3_p = list(Counter(
            self.l3).values())  # counts the elements' frequency
        print("l3_p: {}", l3_p)
        l3_p = (l3_p[1] * 100 / self.total)
        l4_p = list(Counter(
            self.l4).values())  # counts the elements' frequency
        print("l4_p : {}", l4_p)
        l4_p = (l4_p[1] * 100 / self.total)

        r1_p = list(Counter(
            self.r1).values())  # counts the elements' frequency
        print("r1_p : {}", r1_p)
        r1_p = (r1_p[1] * 100 / self.total)
        r2_p = list(Counter(
            self.r2).values())  # counts the elements' frequency
        print("r2_p : {}", r2_p)
        r2_p = (r2_p[1] * 100 / self.total)
        r3_p = list(Counter(
            self.r3).values())  # counts the elements' frequency
        print("r3_p : {}", r3_p)
        r3_p = (r3_p[1] * 100 / self.total)
        r4_p = list(Counter(
            self.r4).values())  # counts the elements' frequency
        print("r4_p : {}", r4_p)
        r4_p = (r4_p[1] * 100 / self.total)

        yvals = [l1_p, l2_p, l3_p, l4_p, r1_p, r2_p, r3_p, r4_p]
        xvals = [
            "Ch 0", "Ch 1", "Ch 3", "Ch 4", "Ch 6", "Ch 7", "Ch 9", "Ch 10"
        ]
        barlist = plt.bar(xvals, yvals)
        barlist[0].set_color('r')
        barlist[1].set_color('r')
        barlist[4].set_color('r')
        barlist[5].set_color('r')
        plt.title("Percentage of Good Events")
        plt.show()
