
import uuid
import django
django.setup()
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from datetime import datetime, timezone
from jinja2 import Template
from django.conf import settings
from common_utils.email.core import send_email
from common_utils.models.common import get_notification_request
from database.models import (
    Tenant,
    EmailSettings,
    NotificationRequest,
    NotificationTemplate
)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%D"

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5}, ignore_result=True,
             name='notification:execute')
def execute(self, payload, **kwargs):
    data: dict = {}
    try:
        
        wa_tenant = Tenant.objects.get(domain='wasteant.com')
        notification_template = NotificationTemplate.objects.get(template_type='registration')
        
        tenant = None
        if Tenant.objects.filter(domain=payload.tenant_domain).exists():
            tenant = Tenant.objects.get(domain=payload.tenant_domain)
            
        notification_request = get_notification_request(
            tenant=tenant,
            notification_template=notification_template,
            request_id=self.request.id,
            request_name='registration',
        )
        
        email_setting = EmailSettings.objects.get(username="notification@wasteant.com")
        msg_template = notification_template.template_body
        
        template = Template(msg_template)
        context = {
            "date": datetime.now().strftime(DATETIME_FORMAT),
            "message_body": payload.message,
            "year": datetime.now().year,
            "company_name": wa_tenant.tenant_name,
            "tenant_logo": payload.tenant_logo,
        }

        rendered_msg = template.render(context)
        send_email(
            username=email_setting.username,
            password=email_setting.password,
            host=email_setting.host,
            port=email_setting.port,
            to_emails=payload.to_emails.split(','),
            msg=rendered_msg,
            subject=payload.subject,
            wa_logo=f"{wa_tenant.logo.path}"
        )
        
        notification_request.request_status = 'sent'
        notification_request.sent_at = datetime.now(tz=timezone.utc)
        notification_request.save()
        
        data.update(
            {
                'action': 'done',
                'time':  datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
                'result': 'success'
            }
        )
    
    except Exception as err:
        if notification_request:
            notification_request.request_status = 'failed'
            notification_request.error_message = f"Error sending email: {err}"
            notification_request.save()
            
        raise ValueError(f"Error sending email: {err}")
    
    return data