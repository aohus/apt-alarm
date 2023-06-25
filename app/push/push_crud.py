from fastapi import Depends, Request
import asyncio

from database import mongodb
from interest.interest_crud import InterestController
from interest.interest_model import InterestModel, Conditions
from .push_model import NoticedAptModel
from utils.apt_scraper import NaverAPTScraper
from utils import slackbot

import logging
import datetime
import re
from typing import List, Dict, Optional

morning = datetime.datetime.now().hour == 9


class PushController:
    async def notice(self) -> List:
        interest_complex_list = await InterestController().read_interest_complex_list(
            "user_id"
        )
        available_apt_list = []
        for complex in interest_complex_list:
            # TODO: (고민) 연속으로 scraping 하면 네이버에서 막아버려서, 단지마다 instance 새로 할당.... 이게 맞나?
            naver_apt_scraper = NaverAPTScraper()
            available_apt = naver_apt_scraper.get_available_apt(complex.complex_id)
            filtered_apt = await self._check_condition(
                complex.complex_id, available_apt
            )
            filtered_apt = await self._check_noticed(filtered_apt)
            available_apt_list.extend(filtered_apt)
            if morning:
                slackbot.post_apt_message(complex.complex_name, filtered_apt)
            elif ":new:" in [apt["noticed_label"] for apt in filtered_apt]:
                new_apt = [
                    apt for apt in filtered_apt if apt["noticed_label"] == ":new:"
                ]
                slackbot.post_apt_message(complex.complex_name, new_apt)
        await self._update_noticed_apt(available_apt_list)
        return available_apt_list

    def _convert_price(self, price: str) -> Optional[float]:
        # 숫자와 ','만 추출
        numbers = re.findall(r"\d+", price)
        if len(numbers) == 1:
            # 억만 있는 경우
            return float(numbers[0])
        elif len(numbers) == 2:
            # 억과 만 모두 있는 경우
            return float(numbers[0]) + float(numbers[1]) / 10
        elif len(numbers) == 3:
            # 억, 천만, 만 순서로 있는 경우
            return (
                float(numbers[0]) + float(numbers[1]) / 10 + float(numbers[2]) / 10000
            )
        else:
            return None

    async def _check_condition(
        self, complex_id: int, available_apt: List[Dict]
    ) -> List[Dict]:
        interest_model = await mongodb.engine.find_one(
            InterestModel, InterestModel.complex_id == complex_id
        )
        conditions = interest_model.conditions
        filtered_apt = []
        for apt in available_apt:
            if conditions.price >= self._convert_price(apt.get("price")):
                filtered_apt.append(apt)
        return filtered_apt

    async def _check_noticed(self, filtered_apt: List[Dict]) -> List[Dict]:
        noticed_apt = await mongodb.engine.find_one(
            NoticedAptModel, NoticedAptModel.user_id == "1"
        )
        for apt in filtered_apt:
            if noticed_apt and apt["item_id"] in noticed_apt.noticed_apt_ids:
                apt["noticed_label"] = ":ballot_box_with_check:"
            else:
                apt["noticed_label"] = ":new:"
        return filtered_apt

    async def _update_noticed_apt(self, noticed_list: List[Dict]):
        noticed_apt = await mongodb.engine.find_one(
            NoticedAptModel, NoticedAptModel.user_id == "1"
        )
        if noticed_apt:
            noticed_apt.noticed_apt_ids = [apt["item_id"] for apt in noticed_list]
        else:
            noticed_apt = NoticedAptModel(
                user_id="1",
                noticed_apt_ids=[apt["item_id"] for apt in noticed_list],
            )
        r = await mongodb.engine.save(noticed_apt)
        # TODO: logging.info()
        return
