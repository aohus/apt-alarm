from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
import re
import math
import requests
import json
from typing import List, Dict, Optional


class NaverAPTScraper:
    def __init__(self):
        self.driver = self._set_chrome_driver()

    def _set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        return driver

    def _search(self, keyword: str):
        url = f"https://m.land.naver.com/search/result/{keyword}"

        # 검색 화면
        self.driver.get(url)
        info = self.driver.find_element(
            By.XPATH, "//*[@id='mapSearch']/script"
        ).get_attribute("innerHTML")
        # filter, lat, lon 값을 추출하는 정규식 패턴
        pattern = r"filter:\s*({[^}]+})"

        # 정규식을 사용하여 값을 추출
        matches = re.search(pattern, info)

        if matches:
            filter_value = matches.group(1)
            # filter 값을 딕셔너리로 구성
            filter_dict = {}
            pairs = re.findall(r"(\w+)\s*:\s*'([^']*)'", filter_value)
            for key, value in pairs:
                filter_dict[key] = value
        else:
            print("해당 패턴을 찾을 수 없습니다.")
        return filter_dict

    def get_complex_info(self, keyword: str) -> List[Dict]:
        # 검색 조건 추출
        filter_dict = self._search(keyword)
        cortarNo = filter_dict.get("cortarNo")
        z = filter_dict.get("z")
        lat = filter_dict.get("lat")
        lon = filter_dict.get("lon")

        lat_margin = 0.118
        lon_margin = 0.111

        btm = float(lat) - lat_margin
        lft = float(lon) - lon_margin
        top = float(lat) + lat_margin
        rgt = float(lon) + lon_margin

        rletTpCd = "APT"  # 아파트
        tradTpCd = "A1:B1"  # 매매:전세 매물 확인

        # 매물 정보 요청 - 축적에 따라, 여러 매물의 묶음 정보가 나오기도 함 ex. [{매물 정보}, {매물 그룹 정보}, ...]
        self.driver.implicitly_wait(5)
        remaked_url = f"https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo={cortarNo}&rletTpCd={rletTpCd}&tradTpCd={tradTpCd}&z={z}&lat={lat}&lon={lon}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&addon=COMPLEX&isOnlyIsale=false"

        self.driver.get(remaked_url)
        info = self.driver.find_element(By.XPATH, "/html/body/pre")
        complex_group_list = (
            json.loads(info.get_attribute("innerHTML")).get("data").get("COMPLEX")
        )

        # 큰 원으로 구성되어 있는 전체 매물 그룹(complex_list)을 load 하여 한 그룹씩 세부 쿼리 진행
        item_list = []
        for complex_group in complex_group_list:
            lgeo = complex_group["lgeo"]
            count = complex_group["count"]
            lat2 = complex_group["lat"]
            lon2 = complex_group["lon"]

            remaked_url2 = f"https://m.land.naver.com/cluster/ajax/complexList?itemId={lgeo}&mapKey=&lgeo={lgeo}&rletTpCd={rletTpCd}&tradTpCd={tradTpCd}&z={z}&lat={lat2}&lon={lon2}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&cortarNo={cortarNo}&isOnlyIsale=false&poiType=CC&preSaleComplexNumber={lgeo}"
            self.driver.get(remaked_url2)
            info = self.driver.find_element(By.XPATH, "/html/body/pre")
            item_list.extend(
                [d for d in json.loads(info.get_attribute("innerHTML")).get("result")]
            )
        return item_list

    def get_available_apt(self, complex_id, trade_type="B1"):
        # trade_type은 추후 필요시 추가 - 매매:A1, 전세:B1, 월세: B2, 매매전세:A1:B1
        url = f"https://m.land.naver.com/complex/info/{complex_id}?tradTpCd={trade_type}&ptpNo=&bildNo=&articleListYN=Y"
        self.driver.get(url)
        info = self.driver.find_element(
            By.CLASS_NAME,
            "article_box.article_box--sale._article",
        )
        html = info.get_attribute("innerHTML")
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", {"class": "item_inner"})

        item_list = []
        if items:
            for item in items:
                title = item.select_one("div > div.title_area > div > strong > em").text
                building = item.select_one(
                    "div > div.title_area > div > strong > span"
                ).text
                type = item.select_one(
                    "div > div.info_area > div.price_area > span"
                ).text
                price = item.select_one(
                    "div > div.info_area > div.price_area > strong"
                ).text
                details = item.select(
                    "div > div.info_area > div.information_area > p.info > span"
                )

                for i, detail in enumerate(details):
                    if i == 0:
                        size, floor, direction = detail.text.split(",")
                    else:
                        describe = detail.text

                item_list.append(
                    (
                        complex_id,
                        title,
                        building,
                        type,
                        price,
                        size,
                        floor,
                        direction,
                        describe,
                    )
                )
        return item_list
