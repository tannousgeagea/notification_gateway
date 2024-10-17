
import os
import json
import time
import uuid
import importlib
from pathlib import Path
from fastapi import Body
from fastapi import Request
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException
from fastapi.routing import APIRoute
from typing_extensions import Annotated
from fastapi import FastAPI, Depends, APIRouter, Request, Header, Response
from typing import Callable, Union, Any, Dict, AnyStr, Optional, List

from events_api.tasks import (
    email
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


class NotificationRequest(BaseModel):
    tenant_domain:Optional[str]=None
    tenant_logo:str
    message:str
    subject:str
    to_emails:str

router = APIRouter(
    prefix="/api/v1",
    tags=["Notification"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)

@router.api_route(
    "/email", methods=["POST"], tags=["Notification"]
)
async def handle_event(
    payload: NotificationRequest = Body(...),
    x_request_id: Annotated[Optional[str], Header()] = None,
) -> ApiResponse:
    
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid request payload")
    
    task = email.core.execute.apply_async(args=(payload,), task_id=x_request_id)
    response_data = {
        "status": "success",
        "task_id": task.id,
        "data": payload.model_dump(),
    }
    
    return ApiResponse(**response_data)


@router.api_route(
    "/email/{task_id}", methods=["GET"], tags=["Notification"], response_model=ApiResponse
)
async def get_event_status(task_id: str, response: Response, x_request_id:Annotated[Optional[str], Header()] = None):
    result = {"status": "received", "task_id": str(uuid.uuid4()), "data": {}}

    return result
