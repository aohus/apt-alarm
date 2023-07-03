from fastapi import FastAPI, APIRouter, HTTPException
import logging
import datetime

from push.push_crud import PushController

router = APIRouter(prefix="/push", tags=["push"])
push_controller = PushController()


@router.patch("", status_code=200)
async def push_alarm():
    start_time = datetime.datetime.now()
    response = await push_controller.notice()
    end_time = datetime.datetime.now()
    logging.info(end_time - start_time)
    if response:
        return
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Bad request",
        )
