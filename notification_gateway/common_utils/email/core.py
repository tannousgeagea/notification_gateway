
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



if __name__ == "__main__":
    
    import django
    django.setup()
    from jinja2 import Template
    from database.models import NotificationTemplate
    
    template = NotificationTemplate.objects.get(template_type='registration')
    msg_template = template.template_body
    
    # msg_template = """
    #     <html>
    #         <body>
    #             <h2>Welcome to Our Service, {{ user_name }}!</h2>
    #             <p>Dear {{ user_name }},</p>
    #             <p>Thank you for joining our platform. We are excited to have you!</p>
    #             <p>Here are some of the features you can explore:</p>
    #             <ul>
    #             <li>Feature 1: {{ feature_1 }}</li>
    #             <li>Feature 2: {{ feature_2 }}</li>
    #             <li>Feature 3: {{ feature_3 }}</li>
    #             </ul>
    #             <p>To get started, click on the button below:</p>
    #             <a href="{{ action_url }}" style="padding:10px 15px; background-color:#007BFF; color:#ffffff; text-decoration:none; border-radius:5px;">Get Started</a>
    #             <p>If you have any questions, feel free to reach out to our support team.</p>
    #             <p>Best regards,<br> The Team</p>
    #         </body>
    #     </html>
    # """

    template = Template(msg_template)
    context = {
        "data": "2024-10-17",
        "message_body": "Hello Tannous",
        "year": 2024
    }

    # Render the template with the context
    rendered_msg = template.render(context)

    # Call the send_html_email function
    send_email(
        username="notification@wasteant.com",
        password="gfnpbttxlzmmphrf",
        to_emails=["tannousgeagea@hotmail.com"],
        host="smtp.office365.com",
        port=587,
        subject="Welcome to Our Service!",
        msg=rendered_msg
    )