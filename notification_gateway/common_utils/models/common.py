
import uuid
import django
django.setup()
from typing import Optional
from database.models import (
    Tenant,
    NotificationRequest,
    NotificationTemplate,
)



def get_notification_request(
    notification_template:NotificationTemplate,
    tenant:Optional[Tenant]=None,
    request_id:Optional[str]=str(uuid.uuid4()),
    request_name:Optional[str]='registration,'
):
    try:
        if NotificationRequest.objects.filter(request_id=request_id).exists():
            return NotificationRequest.objects.get(request_id=request_id)
        
        request = NotificationRequest(
            tenant=tenant if tenant else Tenant.objects.get(domain='wasteant.com'),
            notification_template=notification_template,
            request_id=request_id,
            request_name=request_name,
        )
        
        request.save()
        
        return request
    
    except Exception as err:
        raise ValueError(f"Failed to get notification request. Error: {err}")