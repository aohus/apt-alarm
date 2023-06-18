from fastapi import Depends, Request
from database import mongodb
from utils.apt_scraper import NaverAPTScraper

# from utils import slack_bot


class PushController:
    def update_noticed_apt(self):
        pass

    async def notice(self, complex_id):
        naver_apt_scraper = NaverAPTScraper()
        available_apt_list = naver_apt_scraper.get_available_apt(complex_id)
        await mongodb.client.save_all(available_apt_list)
        # TODO: check logic and send alarm
        pass
