from fastapi import APIRouter, Request
from starlette import status

from complex.complex_model import ComplexModel
from interest.interest_crud import InterestController

router = APIRouter(prefix="/interest/{complex_id}", tags=["interest"])
interest_controller = InterestController()


@router.get("/")
async def read_interest_complex_list(request: Request):
    interest_complex_list = interest_controller.read_interest_complex_list()
    return interest_complex_list


@router.post("/")
async def insert_interest_complex(complex_id: int, complex: ComplexModel):
    response = interest_controller.insert_interest_complex(complex_id, complex)
    return response


@router.patch("/")
async def update_interest_complex(complex_id: int, complex: ComplexModel):
    response = interest_controller.update_interest_complex(complex_id, complex)
    return response


@router.delete("/")
async def delete_interest_complex(complex_id: int, complex: ComplexModel):
    response = interest_controller.delete_interest_complex(complex_id, complex)
    return response
