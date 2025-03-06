
import base64
import requests
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from typing import Optional

def send_email(
    username:str,
    password:str,
    to_emails:str,
    subject:str,
    msg:str,
    host:str,
    port:int,
    wa_logo:str,
    tenant_logo:str,
):

    """
    Sends an HTML email using the provided credentials and server settings.
    
    :param username: SMTP server username (typically the email address)
    :param password: SMTP server password
    :param to_emails: List of recipient email addresses
    :param host: SMTP server host (e.g., 'smtp.gmail.com')
    :param port: SMTP server port (e.g., 587 for TLS)
    :param subject: Subject of the email
    :param msg: HTML content of the email
    """
    
    try:        
        email_msg = MIMEMultipart()
        email_msg['From'] = username
        email_msg['To'] = ', '.join(to_emails)
        email_msg['Subject'] = subject
        email_msg.attach(MIMEText(msg, "html"))
    
        with open(wa_logo, 'rb') as img:
            logo = MIMEImage(img.read())
            logo.add_header('Content-ID', '<logo>')
            email_msg.attach(logo)

        with open(tenant_logo, 'rb') as img:
            logo = MIMEImage(img.read())
            logo.add_header('Content-ID', '<tenant-logo>')
            email_msg.attach(logo)

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_emails, email_msg.as_string())
            
        print(f"Email sent successfully to {to_emails}!")
    
    except Exception as err:
        raise ValueError(f"Failed to send email. Error sending email: {err}")
    

def send_alarm_email(
    username:str,
    password:str,
    to_emails:str,
    subject:str,
    msg:str,
    host:str,
    port:int,
    wa_logo:str,
    tenant_logo:str,
    image_url:Optional[str]=None,
):

    """
    Sends an HTML email using the provided credentials and server settings.
    
    :param username: SMTP server username (typically the email address)
    :param password: SMTP server password
    :param to_emails: List of recipient email addresses
    :param host: SMTP server host (e.g., 'smtp.gmail.com')
    :param port: SMTP server port (e.g., 587 for TLS)
    :param subject: Subject of the email
    :param msg: HTML content of the email
    """
    
    try:        
        email_msg = MIMEMultipart()
        email_msg['From'] = username
        email_msg['To'] = ', '.join(to_emails)
        email_msg['Subject'] = subject
        email_msg.attach(MIMEText(msg, "html"))
    
        with open(wa_logo, 'rb') as img:
            logo = MIMEImage(img.read())
            logo.add_header('Content-ID', '<logo>')
            email_msg.attach(logo)

        with open(tenant_logo, 'rb') as img:
            logo = MIMEImage(img.read())
            logo.add_header('Content-ID', '<tenant-logo>')
            email_msg.attach(logo)

        if image_url:
            response = requests.get(image_url)
            print(response.text)
            if response.status_code == 200:
                image_data = response.content
                image = MIMEImage(image_data)
                image.add_header('Content-ID', "<event-image>")
                email_msg.attach(image)

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_emails, email_msg.as_string())
            
        print(f"Email sent successfully to {to_emails}!")
    
    except Exception as err:
        raise ValueError(f"Failed to send email. Error sending email: {err}")