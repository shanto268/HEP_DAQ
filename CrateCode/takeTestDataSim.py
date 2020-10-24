import os, sys, csv, time


def updateEnvVar():
    r = csv.reader(open('daq_env_var.csv'))  # Here your csv file
    lines = list(r)
    test_num = int(lines[0][1])
    lines[0][1] = test_num + 1
    writer = csv.writer(open('daq_env_var.csv', 'w'))
    writer.writerows(lines)
    return test_num


def plotDiagnostics():
    pass


def saveFile(testNum):
    fileName = "test{}.bin".format(testNum)
    print("{} created!".format(fileName))


def takeData(ev):
    global MUONRATE
    wtime = int(ev) * int(MUONRATE)
    print("Taking data....")
    print("Process will take {} mins".format(wtime))
    time.sleep(2)
    #need to show how many muon events recorded percent of time
    print("{} events recorded....".format(ev))


if __name__ == "__main__":
    MUONRATE = 10
    totalEvents = sys.argv[1]
    doPlot = sys.argv[2]
    doSave = sys.argv[3]
    testNum = updateEnvVar()
    takeData(totalEvents)
    if doPlot:
        plotDiagnostics()
    else:
        pass
    if doSave:
        saveFile(testNum)
    else:
        pass
