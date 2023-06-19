from fastapi import APIRouter, Request, HTTPException, status

from complex.complex_model import ComplexModel
from interest.interest_crud import InterestController

router = APIRouter(prefix="/interest", tags=["interest"])
interest_controller = InterestController()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_interest_complex_list(request: Request):
    interest_complex_list = await interest_controller.read_interest_complex_list()
    return interest_complex_list


@router.post("/{complex_id}", status_code=status.HTTP_201_CREATED)  # created
async def insert_interest_complex(complex_id: int, complex: ComplexModel):
    response = interest_controller.insert_interest_complex(complex_id, complex)
    return response


@router.patch("/{complex_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_interest_complex(complex_id: int, complex: ComplexModel):
    response = interest_controller.update_interest_complex(complex_id, complex)
    return response


@router.delete(
    "/{complex_id}", status_code=status.HTTP_204_NO_CONTENT
)  # 202: action will likely succeed but has not yet been enacted. 204: If the action has been enacted
async def delete_interest_complex(complex_id: int, complex: ComplexModel):
    deleted_complex = await interest_controller.delete_interest_complex(
        complex_id, complex
    )
    if response == 0:
        raise HTTPException(status_code=404, detail="complex_id not found")
    return
