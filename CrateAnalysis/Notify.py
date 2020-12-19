from Emailer import Emailer
import time


class Notify():
    """Docstring for Notify. """
    def __init__(self, ofile=""):
        """TODO: to be defined. """
        self.ofile = ofile

    def email(self, emailList, sms_list, subjectLine, emailContent):
        sender = Emailer(emailList, sms_list, subjectLine, emailContent)
        sender.alert()

    def emailWithPdf(self, emailList, sms_list, subjectLine, emailContent,
                     pfile, cfile):
        sender = Emailer(emailList, sms_list, subjectLine, emailContent)
        sender.sendPdf(pfile, cfile)

    def sendEmail(self):
        emailList = ["sadman-ahmed.shanto@ttu.edu", "nural.akchurin@ttu.edu"]
        sms_list = ['8067900156@sms.mycricket.com']
        events = self.ofile.split("_")[1].split(".bin")[0]
        subjectLine = "File Uploaded to Quanah"
        qpath = "/lustre/work/sshanto/proto1/CAMAC/CrateCode/data_sets"
        command = "Copy the following command into terminal to download the file:\n\nscp sshanto@quanah.hpcc.ttu.edu:{}/{}\n\n".format(
            qpath, self.ofile)
        emailContent = "File {} that has {} events was uploaded to Quanah and can be found at {}.\n {}".format(
            self.ofile, events, qpath, command)
        self.email(emailList, sms_list, subjectLine, emailContent)

    def sendPdfEmail(self, pfile, cfile):
        emailList = ["sadman-ahmed.shanto@ttu.edu", "nural.akchurin@ttu.edu"]
        # emailList = ["sadman-ahmed.shanto@ttu.edu"]
        sms_list = ['8067900156@sms.mycricket.com']
        run = pfile.split("_")[-1].split(".")[0]
        subjectLine = "Report Pdf For Run {}".format(run)
        emailContent = "The analysis report for run {} is attached to this email.".format(
            run)
        self.emailWithPdf(emailList, sms_list, subjectLine, emailContent,
                          pfile, cfile)
