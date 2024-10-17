
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


def send_email(
    username:str,
    password:str,
    to_emails:str,
    subject:str,
    msg:str,
    host:str,
    port:int,
    wa_logo:str,
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

    
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_emails, email_msg.as_string())
            
        print(f"Email sent successfully to {to_emails}!")
    
    except Exception as err:
        raise ValueError(f"Failed to send email. Error sending email: {err}")