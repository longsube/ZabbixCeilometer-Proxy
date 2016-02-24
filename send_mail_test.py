"""
Script to send notification mail to administrators group when VMs are created or deleted
"""

import threading
import readFile
import logging
from logging.handlers import RotatingFileHandler

import argparse 
import smtplib
from email.MIMEText import MIMEText
from email.mime.multipart import MIMEMultipart
from email.Header import Header
from email.Utils import formatdate

# Mail Account
MAIL_ACCOUNT = 'mycloudvnn@vdc.com.vn'
MAIL_PASSWORD = 'Vdc1T@!ma1l'

# Sender Name
SMTP_SERVER = 'smtp.vdc.com.vn'
SMTP_PORT = 25
Check = True

configuration_file="/root/ZabbixCeilometer-Proxy/proxy.conf"
conf_file = readFile.ReadConfFile(configuration_file)
recieve_emails = conf_file.read_option('recieve_users', 'emails')


def send(instance_name, instance_id, tenant_name, action, encoding='utf-8'):
    session = None
    if 'create' in action:
        bd = "Tao VM {0}.\n ID: {1} \n Tenant: {2}".format(instance_name, instance_id, tenant_name)
    elif 'delete' in action:
 #   else:
        bd = "Xoa VM {0}.\n ID: {1} \n Tenant: {2}".format(instance_name, instance_id, tenant_name)
    else:
        return    
    msg = MIMEText(bd, 'plain', encoding)
    subject = "Test mail tao VM"
    msg['Subject'] = Header(subject, encoding)
#    msg['From'] = Header(SENDER_NAME, encoding)
    msg['To'] = recieve_emails
    recipients = recieve_emails.split(',')
    msg['Date'] = formatdate()
    try:
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        if Check:
            session.ehlo()
            session.starttls()
            session.ehlo()
            session.login(MAIL_ACCOUNT, MAIL_PASSWORD)
        session.sendmail(MAIL_ACCOUNT, recipients, msg.as_string())
    except Exception as e:
        raise e
    finally:
        # close session
        if session:
            session.quit()


if __name__ == '__main__':
    """
    recipient = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]
    """
    argp = argparse.ArgumentParser(description='Lay thong tin gui mail')
    argp.add_argument('instance_name', type=str, help='Recipient')
    argp.add_argument('instance_id', type=str, help='Subject')
    argp.add_argument('tenant_name', type=str, help='Body')
    argp.add_argument('action', type=str, help='Body') 
    args = argp.parse_args()

    send(
        instance_name=args.instance_name,
        instance_id=args.instance_id,
        tenant_name=args.tenant_name,
        action=args.action)
