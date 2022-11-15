#!/usr/bin/python
#
# Purpose: Python script to send e-mails and attachments via SMTP authentication using TLS
# Author: Bohdan Jakym, bohdan.jakym@kyndryl.com
# CHANGE HISTORY
# --------------
# v1.0 - Baseline

# Import modules
import sys, getopt, os.path
import smtplib
import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

# Read credentials from config file
def get_credentials(conf_file):
    d = {}
    with open(conf_file) as f:
        for line in f:
            (key, val) = line.strip().split("=", 1)
            if key == "smtp_pwd":
                val_bytes = base64.b64decode(val)
                val = val_bytes.decode("ascii").strip()
            d[key] = val
    return d

# Send e-mail via SMTP Auth with TLS
def send_mail(send_from, send_user, send_pwd, send_server, send_port, send_to, subject, text, files=None):
    assert isinstance(send_to, list)
    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    for f in files or []:
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=os.path.basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP(send_server, send_port)
    smtp.ehlo()
    smtp.starttls()
    smtp.login(send_user, send_pwd)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

# Main function
def main(argv):
   # Handle input parameters, exit 2 if wrong argument is used
   try:
      opts, args = getopt.getopt(argv,"hc:r:s:m:f:",["conf_file=","recepients=","subject=","message=","files="])
   except getopt.GetoptError:
      print("send_e-mail.py -c <config_file> -r <recepient1,...,recepientN> -s <subject> -m <message> -f <file1,...,fileN>")
      sys.exit(1)
   for opt, arg in opts:
      if opt == '-h':
         print("send_e-mail.py -c <config_file> -r <recepient1,...,recepientN> -s <subject> -m <message> -f <file1,...,fileN>")
         sys.exit()
      elif opt in ("-c", "--config_file"):
         config_file = arg
      elif opt in ("-r", "--recepients"):
         recipients = arg.split(",")
      elif opt in ("-s", "--subject"):
         email_subject = arg
      elif opt in ("-m", "--message"):
         email_message = arg
      elif opt in ("-f", "--files"):
         file_attachments = arg.split(",")

   dict_cred = {}
   if os.path.exists(config_file): 
     dict_cred = get_credentials(config_file)
   else:
     print("ERROR: specified configuration does not exist.")
     sys.exit(2)

   try:
     send_mail(dict_cred['sender'], dict_cred['smtp_user'], dict_cred['smtp_pwd'], dict_cred['smtp_server'], dict_cred['smtp_port'], recipients, email_subject, email_message, file_attachments)
   except:
     send_mail(dict_cred['sender'], dict_cred['smtp_user'], dict_cred['smtp_pwd'], dict_cred['smtp_server'], dict_cred['smtp_port'], recipients, email_subject, email_message)

# Main
if __name__ == "__main__":
   main(sys.argv[1:])