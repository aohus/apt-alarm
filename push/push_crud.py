from fastapi import Depends, Request
from database import mongodb

from interest.interest_crud import InterestController
from .push_model import NoticedAptModel
from utils.apt_scraper import NaverAPTScraper
from utils import slack_bot

import logging
from typing import List

# from utils import slack_bot


class PushController:
    def make_push_message(self, available_apt_list):
        message = ""

    async def _update_noticed_apt(self, noticed_list: List):
        noticed_list_model = NoticedAptModel(
            user_id="1",
            noticed_apt_ids=[apt["item_id"] for apt in noticed_list],
        )
        r = await mongodb.engine.save(noticed_list_model)
        print(r)
        # TODO: logging.info()
        return

    async def notice(self, complex_id):
        interest_complex_list = InterestController().read_interest_complex_list(
            "user_id"
        )
        naver_apt_scraper = NaverAPTScraper()

        available_apt_list = []
        for complex in interest_complex_list:
            available_apt_list.extend(
                naver_apt_scraper.get_available_apt(complex.get(complex_id))
            )
        await self._update_noticed_apt(available_apt_list)

        # TODO: check logic and send alarm
        slack_bot.info(str(available_apt_list))
        return available_apt_list
