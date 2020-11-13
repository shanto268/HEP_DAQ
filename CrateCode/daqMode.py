#usage: ./daqMode.py numEventsPerRun sleepTimeBetweenEventsInMinutes

import os, time, sys


def takeData(eventNum, sleepTime):
    os.system("python takeData.py {}".format(eventNum))
    print("Sleeping for {} minutes".format(sleepTime))
    time.sleep(float(sleepTime) * 60)


if __name__ == "__main__":
    eventNum = sys.argv[1]
    sleepTime = sys.argv[2]
    while True:
        takeData(eventNum, sleepTime)
