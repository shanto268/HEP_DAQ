from Emailer import Emailer
import time


class Notify():
    """Docstring for Notify. """
    def __init__(self, ofile):
        """TODO: to be defined. """
        self.ofile = ofile
        self.sendEmail

    def email(self, emailList, sms_list, subjectLine, emailContent):
        sender = Emailer(emailList, sms_list, subjectLine, emailContent)
        sender.alert()

    def sendEmail(self):
        emailList = ["sadman-ahmed.shanto@ttu.edu"]
        sms_list = ['8067900156@sms.mycricket.com']
        subjectLine = "File Uploaded to Quanah"
        qpath = "/lustre/work/sshanto/proto1/CAMAC/CrateCode/data_sets"
        command = "Copy the following command into terminal to download the file:\n scp sshanto@quanah.hpcc.ttu.edu:{}/{} .".format(
            qpath, ofile)
        emailContent = "File {} was uploaded to Quanah and can be found at {}.\n  {}.".format(
            self.ofile, qpath, command)
        self.email(emailList, sms_list, subjectLine, emailContent)
