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
MAIL_ACCOUNT = 
MAIL_PASSWORD = 

# Sender Name
SMTP_SERVER = 
SMTP_PORT = 25
Check = True

configuration_file="/root/ZabbixCeilometer-Proxy/proxy.conf"
conf_file = readFile.ReadConfFile(configuration_file)
recieve_emails = conf_file.read_option('recieve_users', 'emails')


def send(instance_name, instance_id, instance_type, public_ip, tenant_name, ram, root_disk, vcpu, host, action, encoding='utf-8'):
    session = None
    if 'create' in action:
        bd = """<html>
                    <p><b>VM IS CREATED</b></p>
                    <p>Name: <b><i>{0}</i></b></p>
                    <p>ID: <b><i>{1}</i></b></p>
                    <p>Flavor: <b><i>{2} (CPU: {3}, RAM: {4} MB, Root_Disk: {5} GB)</i></b></p>
                    <p>Public IP: <b><i>{6}</i></b></p>
                    <p>Host: <b><i>{7}</i></b></p>
                    <p>Tenant: <b><i>{8}</i></b></p></html>""".format(instance_name, instance_id, instance_type, vcpu, ram, root_disk, public_ip, host, tenant_name)
        subject = "Create new VM"
    elif 'delete' in action:
 #   else:
        bd = """<html>
                    <p><b>VM IS DESTROYED</b></p>
                    <p>Name: <b><i>{0}</i></b></p>
                    <p>ID: <b><i>{1}</i></b></p>
                    <p>Flavor: <b><i>{2} (CPU: {3}, RAM: {4} MB, Root_Disk: {5} GB)</i></b></p>
                    <p>Host: <b><i>{6}</i></b></p>
                    <p>Tenant: <b><i>{7}</i></b></p></html>""".format(instance_name, instance_id, instance_type,vcpu, ram, root_disk, host, tenant_name)
        subject = "Delete VM"
    else:
        return    
    msg = MIMEText(bd, 'html', encoding)
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
