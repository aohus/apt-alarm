from fastapi import FastAPI, APIRouter, Request
from configs.config import BASE_DIR

import re
import logging
from datetime import datetime

from push.push_crud import PushController

router = APIRouter(prefix="/push", tags=["push"])
push_controller = PushController()


@router.patch("", status_code=200)
async def push_alarm():
    r = await push_controller.notice(104223)
    return
