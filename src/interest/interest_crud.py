from fastapi import Depends, Request

from database import mongodb
from utils.apt_scraper import NaverAPTScraper
from complex.complex_model import ComplexModel
from .interest_model import InterestModel, Conditions
from typing import List


class InterestController:
    async def read_interest_complex_list(self, request: Request) -> List[InterestModel]:
        if not "회원":
            return  # TODO: 로그인/회원가입 화면

        if await mongodb.engine.find_one(
            InterestModel, InterestModel.user_id == "1"
        ):  # TODO: 로그인 만들기
            complex_list = await mongodb.engine.find(
                InterestModel, InterestModel.user_id == "1"
            )
            return complex_list
        else:
            return

    async def insert_interest_complex(self, complex_id: int, complex: ComplexModel):
        registered_complex = await mongodb.engine.find_one(
            InterestModel,
            (InterestModel.user_id == "1") & (InterestModel.complex_id == complex_id),
        )
        if registered_complex:
            return

        interest_model = InterestModel(
            user_id="1",
            complex_id=complex_id,
            complex_name=complex.complex_name,
            conditions=Conditions(min_size=10, min_floors=1, max_floors=10, price=4),
        )
        r = await mongodb.engine.save(interest_model)  # 각 모델 인스턴스를 DB에 저장한다.
        return r

    async def update_interest_complex(self, complex_id: int, complex: ComplexModel):
        # TODO : user_id, complex_id 같은 것 있으면 지우고 추가, 뒤집어 쓰기
        interest_model = InterestModel(
            user_id="1",
            complex_id=complex_id,
            complex_name=complex.complex_name,
        )
        r = await mongodb.engine.save(interest_model)
        return r

    async def delete_interest_complex(self, complex_id: int, complex: ComplexModel):
        r = await mongodb.engine.remove(
            InterestModel,
            (InterestModel.user_id == "1") & (InterestModel.complex_id == complex_id),
        )
        return r
