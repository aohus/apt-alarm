from fastapi import APIRouter, Request, HTTPException, status

from complex.complex_model import ComplexModel
from interest.interest_crud import InterestController
import logging

router = APIRouter(prefix="/interest", tags=["interest"])
interest_controller = InterestController()


@router.get("/", status_code=status.HTTP_200_OK)
async def read_interest_complex_list(request: Request):
    response = await interest_controller.read_interest_complex_list(request)
    logging.info(f"read interest apt response: {response}")
    if response:
        return response
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Bad request",
        )


@router.post("/{complex_id}", status_code=status.HTTP_201_CREATED)  # created
async def insert_interest_complex(complex_id: int, complex: ComplexModel):
    response = await interest_controller.insert_interest_complex(complex_id, complex)
    logging.info(f"insert interest apt response: {response}")
    if response:
        return response
    else:
        raise HTTPException(
            status_code=400,
            detail=f"이미 관심리스트에 있는 아파트단지입니다. 다른 단지를 추가해주세요.",
        )


# TODO: 기능구현 + 프론트
@router.patch("/{complex_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_interest_complex(complex_id: int, complex: ComplexModel):
    response = await interest_controller.update_interest_complex(complex_id, complex)
    logging.info(f"update interest apt response: {response}")
    if response:
        return response
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Bad request",
        )


@router.delete(
    "/{complex_id}", status_code=status.HTTP_204_NO_CONTENT
)  # 202: action will likely succeed but has not yet been enacted. 204: If the action has been enacted
async def delete_interest_complex(complex_id: int, complex: ComplexModel):
    response = await interest_controller.delete_interest_complex(complex_id, complex)
    logging.info(f"delete interest apt response: {response}")
    if response == 0:
        raise HTTPException(
            status_code=404,
            detail=f"complex_id:{complex_id} / complex_name:{complex.get('complex_name')} not found",
        )
    return response
