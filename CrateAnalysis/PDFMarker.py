import os


def getPDF(runNum, pdfName):
    try:
        os.system("./cpdf -add-text \"Run {}\" -topright 8  {} -o {}".format(
            runNum, pdfName, pdfName))
    except:
        os.system("cpdf -add-text \"Run {}\" -topright 8  {} -o {}".format(
            runNum, pdfName, pdfName))


if __name__ == "__main__":
    getPDF(100, "events_data_frame_100.pdf")
