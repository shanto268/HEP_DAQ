import smtplib
import datetime as time
import io
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from secrets import passwd, email_id, port_id
from email.mime.application import MIMEApplication

#Email vairables
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = port_id
GMAIL_USERNAME = email_id
GMAIL_PASSWORD = passwd


class Emailer:
    def __init__(self, email_list, text_list, subjectLine, emailContent):
        self.email_list = email_list
        self.text_list = text_list
        self.subjectLine = subjectLine
        self.emailContent = emailContent
        self.path2pdf = ""

    def send_email_pdf_only(self, path_to_pdf, path2csv, subject, message,
                            destination):
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        # Craft message (obj)
        msg = MIMEMultipart()

        message = f'{message}\n\nSent from APDL_DAQ_Machine and Quanah.'
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = destination
        # Insert the text to the msg going by e-mail
        msg.attach(MIMEText(message, "plain"))
        # Attach the pdf to the msg going by e-mail
        with open(path_to_pdf, "rb") as f:
            #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
            attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition',
                          'attachment',
                          filename=str(path_to_pdf))
        msg.attach(attach)

        # send msg
        server.send_message(msg)
        server.close()

    def send_email_pdf_figs(self, path_to_pdf, path2csv, subject, message,
                            destination):
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        # Craft message (obj)
        msg = MIMEMultipart()

        message = f'{message}\n\nSent from APDL_DAQ_Machine and Quanah.'
        msg['Subject'] = subject
        msg['From'] = GMAIL_USERNAME
        msg['To'] = destination
        # Insert the text to the msg going by e-mail
        msg.attach(MIMEText(message, "plain"))
        # Attach the pdf to the msg going by e-mail
        with open(path_to_pdf, "rb") as f:
            #attach = email.mime.application.MIMEApplication(f.read(),_subtype="pdf")
            attach = MIMEApplication(f.read(), _subtype="pdf")
        attach.add_header('Content-Disposition',
                          'attachment',
                          filename=str(path_to_pdf))
        msg.attach(attach)

        csvName = path2csv.split("/")[-1]
        with open(path2csv, 'rb') as file:
            # Attach the file with filename to the email

            csvFile = MIMEApplication(file.read(), _subtype="csv")
            csvFile.add_header('Content-Disposition',
                               'attachment',
                               filename=csvName)
            msg.attach(csvFile)
        # send msg
        server.send_message(msg)
        server.close()

    def alert(self):
        emails = self.email_list
        incidentTime = time.datetime.now()
        self.emailContent += "\n incident time {}".format(incidentTime)
        #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
        for email in emails:
            print("Emailing {}".format(email))
            self.sendmail(email, self.subjectLine, self.emailContent)

    def sendPdf(self, path2pdf, path2csv):
        self.path2pdf = path2pdf
        emails = self.email_list
        #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
        for email in emails:
            print("Emailing {}".format(email))
            self.send_email_pdf_figs(self.path2pdf, path2csv, self.subjectLine,
                                     self.emailContent, email)

    def sendPdfOnly(self, path2pdf, path2csv):
        self.path2pdf = path2pdf
        emails = self.email_list
        #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
        for email in emails:
            print("Emailing {}".format(email))
            self.send_email_pdf_only(self.path2pdf, path2csv, self.subjectLine,
                                     self.emailContent, email)

    def sendmail(self, recipient, subject, content):
        #Headers
        headers = [
            "From:" + GMAIL_USERNAME, "Subject:" + subject, "To: " + recipient,
            "MIME-Version: 1.0", "Content-Type: text/plain"
        ]
        headers = "\r\n".join(headers)

        #Connect to Gmail Server
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.ehlo()
        session.starttls()
        session.ehlo()

        #Gmail Login
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        #Send email then exit
        session.sendmail(GMAIL_USERNAME, recipient,
                         headers + "\r\n\r\n" + content)
        # session.quit()
        session.close()

    def sendtext(self, recipient, subject, content):
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.starttls()
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject + "\n"
        body = content + "\n"
        # and then attach that body furthermore you can also send html content.
        msg.attach(MIMEText(body, 'plain'))
        sms = msg.as_string()
        session.sendmail(GMAIL_USERNAME, recipient, sms)
        session.quit

    def alert(self):
        emails = self.email_list
        incidentTime = time.datetime.now()
        self.emailContent += "\n incident time {}".format(incidentTime)
        #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
        for email in emails:
            print("Emailing {}".format(email))
            self.sendmail(email, self.subjectLine, self.emailContent)

    def alert_text(self):
        texts = self.text_list
        incidentTime = time.datetime.now()
        self.emailContent += "\n incident time {}".format(incidentTime)
        #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
        for text in texts:
            print("Texting {}".format(text))
            self.sendtext(text, self.subjectLine, self.emailContent)

    def phased_alert(self):
        emails = self.email_list
        incidentTime = time.datetime.now()
        for email in emails:
            print("Emailing {}".format(email))
            self.sendmail(email, self.subjectLine, self.emailContent)
