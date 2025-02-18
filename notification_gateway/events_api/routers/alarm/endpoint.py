
import os
import json
import time
import uuid
import django
django.setup()
import traceback
import importlib
from pathlib import Path
from fastapi import Body
from fastapi import Request
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.routing import APIRoute
from typing_extensions import Annotated
from fastapi import status
from fastapi import FastAPI, Depends, APIRouter, Request, Header, Response
from typing import Callable, Union, Any, Dict, AnyStr, Optional, List

from django.core.exceptions import ObjectDoesNotExist
from database.models import NotificationRequest

from events_api.tasks import (
    alarm
)

class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler


class ApiResponse(BaseModel):
    status: str
    task_id: str
    data: Optional[Dict[AnyStr, Any]] = None


class ApiNotificationRequest(BaseModel):
    tenant_domain:Optional[str]=None
    timestamp:datetime
    location:str
    region:str
    severity_level:str
    event_type:str
    alarm_description:str
    delivery_id:Optional[str]=None
    image_url:Optional[str]=None
    video_url:Optional[str]=None
    to_emails:Optional[str]=None

router = APIRouter(
    prefix="/api/v1",
    tags=["Alarm Notification"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)

@router.api_route(
    "/alarm/email", methods=["POST"], tags=["Alarm Notification"]
)
async def handle_event(
    payload: ApiNotificationRequest = Body(...),
    x_request_id: Annotated[Optional[str], Header()] = None,
) -> ApiResponse:
    
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid request payload")
    
    task = alarm.core.execute.apply_async(args=(payload,), task_id=x_request_id)
    response_data = {
        "status": "success",
        "task_id": task.id,
        "data": payload.model_dump(),
    }
    
    return ApiResponse(**response_data)


@router.api_route(
    "/alarm/email/{task_id}", methods=["GET"], tags=["Alarm Notification"]
)
def get_event_status(
    task_id: str, 
    response: Response, 
    ):
    results = {}
    try:
        
        if not NotificationRequest.objects.filter(request_id=task_id).exists():
            results["error"] = {
                "status_code": "not found",
                "status_description": f"Task id {task_id} not found",
                "detail": f"Invalid task id {task_id}",
            }
            
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
        
        request_notification = NotificationRequest.objects.get(request_id=task_id)
        results.update(
            {
                "status": request_notification.request_status,
                "time": request_notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "task_id": task_id,
                "error": request_notification.error_message,
                
            }
        )
        
    except ObjectDoesNotExist as e:
        results['error'] = {
            'status_code': "non-matching-query",
            'status_description': f'Matching query was not found',
            'detail': f"matching query does not exist. {e}"
        }

        response.status_code = status.HTTP_404_NOT_FOUND
        
    except HTTPException as e:
        results['error'] = {
            "status_code": "not found",
            "status_description": "Request not Found",
            "detail": f"{e}",
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
    
    except Exception as e:
        results['error'] = {
            'status_code': 'server-error',
            "status_description": "Internal Server Error",
            "detail": traceback.format_exc(),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return results
