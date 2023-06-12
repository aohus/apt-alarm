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
from typing import Dict, Optional


class NaverAPTScraper:
    def __init__(self):
        driver = self._set_chrome_driver()

    def _set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        return driver

    def search(self, keyword: str) -> Dict[str:Optional]:
        keyword = "이의동"  # TODO
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

    def get_apt_info(self, filter_dict):
        # 검색 조건 추출
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

        # 매물 정보 요청
        self.driver.implicitly_wait(5)
        remaked_url = f"https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo={cortarNo}&rletTpCd={rletTpCd}&tradTpCd={tradTpCd}&z={z}&lat={lat}&lon={lon}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&addon=COMPLEX&isOnlyIsale=false"
        self.driver.get(remaked_url)
        info = self.driver.find_element(By.XPATH, "/html/body/pre")
        complex_list = (
            json.loads(info.get_attribute("innerHTML")).get("data").get("COMPLEX")
        )

        # 큰 원으로 구성되어 있는 전체 매물그룹(values)을 load 하여 한 그룹씩 세부 쿼리 진행
        for complex in complex_list:
            lgeo = complex["lgeo"]
            count = complex["count"]
            lat2 = complex["lat"]
            lon2 = complex["lon"]
            # if count > 1:
            remaked_url2 = f"https://m.land.naver.com/cluster/ajax/complexList?itemId={lgeo}&mapKey=&lgeo={lgeo}&rletTpCd={rletTpCd}&tradTpCd={tradTpCd}&z={z}&lat={lat2}&lon={lon2}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&cortarNo={cortarNo}&isOnlyIsale=false&poiType=CC&preSaleComplexNumber={lgeo}"
            self.driver.get(remaked_url2)
            info = self.driver.find_element(By.XPATH, "/html/body/pre")
            item_list = json.loads(info.get_attribute("innerHTML")).get("result")

            complex_models = []
            for item in item_list:
                complex_model = ComplexModel(
                    item_id=item["hscpNo"],
                    apt_name=item["hscpNm"],
                    type="complex",
                    total_dong_count=item["totDongCnt"],
                    total_apt_count=item["totHsehCnt"],
                    approve_date=item["useAprvYmd"],
                    deal_count=item["dealCnt"],
                    lease_count=item["leaseCnt"],
                    min_space=item["minSpc"],
                    max_space=item["maxSpc"],
                    min_deal_price=item["dealPrcMin"],
                    max_deal_price=item["dealPrcMax"],
                    min_lease_price=item["leasePrcMin"],
                    max_lease_price=item["leasePrcMax"],
                )
                complex_models.append(complex_model)
            await mongodb.engine.save_all(complex_models)  # 각 모델 인스턴스를 DB에 저장한다.
