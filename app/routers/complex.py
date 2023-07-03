from fastapi import FastAPI, APIRouter, Request
from configs.config import BASE_DIR
from complex.complex_crud import ComplexController

# TODO: 분리 후 삭제
import logging
from fastapi.templating import Jinja2Templates
from configs.config import BASE_DIR

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/complex", tags=["complex"])
complex_controller = ComplexController()


# TODO: 분리
@router.get("/search", status_code=200)
async def get_complex_list(request: Request):
    complex_list = await complex_controller.search_complex(request)
    logging.info(f"complex_list: {complex_list}")
    return templates.TemplateResponse(
        "main.html", context={"request": request, "complexes": complex_list}
    )
