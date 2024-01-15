# TODO: 분리 후 삭제
from configs.config import BASE_DIR
from fastapi import APIRouter
from fastapi import Request
from fastapi.templating import Jinja2Templates
from utils.apt_scraper import NaverAPTScraper

from complex.complex_crud import ComplexController

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/complex", tags=["complex"])
complex_controller = ComplexController(NaverAPTScraper())


# TODO: 분리
@router.get("/search", status_code=200)
async def get_complex_list(request: Request):
    complex_list = await complex_controller.search_complex(request)
    return templates.TemplateResponse(
        "main.html", context={"request": request, "complexes": complex_list}
    )
