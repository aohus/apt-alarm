import logging

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from configs.config import BASE_DIR
from database import mongodb

# from .dependencies import get_query_token, get_token_header
from interest.interest_model import InterestModel
from internal import admin
from routers import complex
from routers import interest
from routers import push

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# app = FastAPI(dependencies=[Depends(get_query_token)])
app = FastAPI()

app.include_router(complex.router)
app.include_router(interest.router)
app.include_router(push.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    context = {"request": request, "title": "부동산 정보"}
    return templates.TemplateResponse("main.html", context=context)


@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request):
    # if login :
    interest_complexes = await mongodb.engine.find(
        InterestModel, InterestModel.user_id == "1"
    )
    context = {"request": request, "title": "My Page", "complexes": interest_complexes}
    return templates.TemplateResponse("mypage.html", context=context)


@app.on_event("startup")
async def on_app_start():
    """
    before app starts
    """
    await mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    """
    after app shutdown
    """
    await mongodb.close()
