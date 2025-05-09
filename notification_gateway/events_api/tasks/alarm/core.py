
import uuid
import pytz
import django
django.setup()
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from celery import shared_task
from datetime import datetime, timezone
from jinja2 import Template
from django.conf import settings
from common_utils.email.core import send_alarm_email
from common_utils.models.common import get_notification_request
from database.models import (
    Tenant,
    EmailSettings,
    NotificationRequest,
    NotificationTemplate,
    Recipient,
    TenantStorageSettings,
)

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

@shared_task(bind=True,autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5}, ignore_result=True,
             name='alarm:execute')
def execute(self, payload, **kwargs):
    data: dict = {}
    try:
        
        wa_tenant = Tenant.objects.get(domain='wasteant.com')
        notification_template = NotificationTemplate.objects.get(template_type='alarm')
        
        tenant = Tenant.objects.filter(domain=payload.tenant_domain).first()
        if not tenant:
            raise ObjectDoesNotExist(f"❌ Tenant {payload.tenant_domain} does not exist.") 
            
        tenant_tz = pytz.timezone(tenant.timezone)
        tenant_storage_settings = TenantStorageSettings.objects.filter(tenant=tenant).first()
        active_recipients = list(Recipient.objects.filter(tenant=tenant, is_active=True).values_list('email', flat=True))
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
            "date": datetime.now().astimezone(tenant_tz).strftime(DATETIME_FORMAT),
            "year": datetime.now().year,
            "tenant_logo": tenant.logo.url,
            "company_name": wa_tenant.tenant_name,
            "timestamp": payload.timestamp.strftime(DATETIME_FORMAT),
            "location": payload.location,
            "region": payload.region,
            "severity_level": payload.severity_level,
            "event_type": payload.event_type,
            "alarm_description": payload.alarm_description,
            "delivery_id": payload.delivery_id if payload.delivery_id else 'Keine Zuordnung',
            "image_url": f"https://wacoreblob.blob.core.windows.net/{payload.image_url}?{tenant_storage_settings.account_key}",
        }

        if payload.delivery_id:
            context.update(
                {
                    "delivery_url": f"https://{tenant.domain}/acceptancontrol/single_event?delivery_id={payload.delivery_id}",
                    "delivery_url_text": f"Weiterleitung zum Dashboard (Tabelle: Anlieferung)"
                }
            )

        if payload.event_uid:
            event_uid = payload.event_uid
        
        else:
            event_uid = payload.image_url.split("_")[-1].split(".jpg")[0]

        if event_uid:
            context.update(
                {
                    "dashboard_url": f"https://{tenant.domain}/alarmsmanagement/single_event?alarm_id={event_uid}",
                    "dashboard_text": f"Weiterleitung zum Dashboard (Tabelle: Aufälligkeit)"
                }
            )

        rendered_msg = template.render(context)
        send_alarm_email(
            username=email_setting.username,
            password=email_setting.password,
            host=email_setting.host,
            port=email_setting.port,
            to_emails=active_recipients,
            msg=rendered_msg,
            subject=f"{notification_template.subject}: {payload.event_type} [{payload.severity_level}]",
            wa_logo=f"{wa_tenant.logo.path}",
            tenant_logo=tenant.logo.path,
            image_url=f"https://wacoreblob.blob.core.windows.net/{payload.image_url}?{tenant_storage_settings.account_key}",
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