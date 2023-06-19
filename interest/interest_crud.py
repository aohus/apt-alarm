from fastapi import Depends, Request

from database import mongodb
from utils.apt_scraper import NaverAPTScraper
from complex.complex_model import ComplexModel
from .interest_model import InterestModel
from typing import List


class InterestController:
    async def read_interest_complex_list(self, request: Request) -> List[InterestModel]:
        if not "회원":
            return  # TODO: 로그인/회원가입 화면

        if await mongodb.engine.find_one(
            InterestModel, InterestModel.user_id == "1"
        ):  # TODO: 로그인 만들기
            # 키워드에 대해 수집된 데이터가 DB에 존재한다면 해당 데이터를 사용자에게 보여준다.
            complex_list = await mongodb.engine.find(
                InterestModel, InterestModel.user_id == "1"
            )
            # context = {"request": request, "user_id": 1, "complex_list": complex_list}
            print(complex_list)
            return complex_list
        else:
            return "no list"

    async def insert_interest_complex(self, complex_id: int, complex: ComplexModel):
        registered_complex = await mongodb.engine.find_one(
            InterestModel,
            (InterestModel.user_id == "1") & (InterestModel.complex_id == complex_id),
        )
        if registered_complex:
            return {"already added"}

        interest_model = InterestModel(
            user_id="1",
            complex_id=complex_id,
            complex_name=complex.complex_name,
            conditions=Conditions(min_size=10, min_floors=1, max_floors=10, price=4),
        )
        await mongodb.engine.save(interest_model)  # 각 모델 인스턴스를 DB에 저장한다.
        return {"success"}

    async def update_interest_complex(self, complex_id: int, complex: ComplexModel):
        # TODO : user_id, complex_id 같은 것 있으면 지우고 추가, 뒤집어 쓰기
        interest_model = InterestModel(
            user_id="1",
            complex_id=complex_id,
            complex_name=complex.complex_name,
        )
        await mongodb.engine.save(interest_model)
        return "good"

    async def delete_interest_complex(slef, complex_id: int, complex: ComplexModel):
        if await mongodb.engine.remove(
            InterestModel,
            (InterestModel.user_id == "1") & (InterestModel.complex_id == complex_id),
        ):
            return {"good"}
        else:
            return {"no list"}
