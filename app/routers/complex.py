from fastapi import FastAPI, APIRouter, Request
from configs.config import BASE_DIR
from complex.complex_crud import ComplexController


router = APIRouter(prefix="/complex", tags=["complex"])
complex_controller = ComplexController()


@router.get("/search")
def get_complex_list(request: Request):
    complex_list = complex_controller.search_complex(request)
    return complex_list
