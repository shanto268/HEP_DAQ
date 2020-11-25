import glob
import os
import json


# get latest file
def getLatestFile(path):
    list_of_files = glob.glob(
        '{}/*'.format(path))  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


# match latest file with local record
def checkValidity(latest_file, path):
    with open("record.json") as f:
        data = json.load(f)
        file = path + "/" + data['name']
        print(file)
    if file == latest_file:
        pass
    else:
        os.system("echo analyze the file")
        data['name'] = latest_file
        updateLocalRecord(file, data)


# update the local record
def updateLocalRecord(latest_file, data):
    #overwrite local record with the latest file name
    with open('record.json', 'w') as outfile:
        json.dump(data, outfile)


if __name__ == "__main__":
    path = "/Users/sshanto/hep/hep_daq/CAMAC/CrateAnalysis/processed_data"
    lf = getLatestFile(path)
    checkValidity(lf, path)
