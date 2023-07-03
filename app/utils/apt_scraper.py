from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

import re, math, json
import logging
from typing import List, Dict, Optional
from . import slackbot


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

    def _make_url(self, search_type: str, **kwargs):
        var = kwargs
        if search_type == "dong":
            return f"https://m.land.naver.com/search/result/{var.get('keyword')}"
        elif search_type == "cluster_group":
            cortarNo = var.get("cortarNo")
            z = var.get("z")
            lat = var.get("lat")
            lon = var.get("lon")

            lat_margin = 0.118
            lon_margin = 0.111
            btm = float(lat) - lat_margin
            lft = float(lon) - lon_margin
            top = float(lat) + lat_margin
            rgt = float(lon) + lon_margin

            rletTpCd = "APT"  # 매물 타입 아파트
            tradTpCd = "A1:B1"  # 매매:전세 / 월세=B2
            return (
                "https://m.land.naver.com/cluster/clusterList?view=atcl"
                f"&cortarNo={cortarNo}"
                f"&rletTpCd={rletTpCd}"
                f"&tradTpCd={tradTpCd}"
                f"&z={z}"
                f"&lat={lat}"
                f"&lon={lon}"
                f"&btm={btm}"
                f"&lft={lft}"
                f"&top={top}"
                f"&rgt={rgt}"
                f"&addon=COMPLEX&isOnlyIsale=false"
            )
        elif search_type == "cluster":
            cortarNo = var.get("cortarNo")
            z = var.get("z")
            lgeo = var.get("lgeo")
            lat2 = var.get("lat")
            lon2 = var.get("lon")

            lat_margin = 0.118
            lon_margin = 0.111
            btm = float(lat) - lat_margin
            lft = float(lon) - lon_margin
            top = float(lat) + lat_margin
            rgt = float(lon) + lon_margin

            rletTpCd = "APT"
            tradTpCd = "A1:B1"

            return (
                "https://m.land.naver.com/cluster/ajax/complexList"
                f"?itemId={lgeo}"
                f"&mapKey="
                f"&lgeo={lgeo}"
                f"&rletTpCd={rletTpCd}"
                f"&tradTpCd={tradTpCd}"
                f"&z={z}"
                f"&lat={lat2}"
                f"&lon={lon2}"
                f"&btm={btm}"
                f"&lft={lft}"
                f"&top={top}"
                f"&rgt={rgt}"
                f"&cortarNo={cortarNo}"
                f"&isOnlyIsale=false&poiType=CC"
                f"&preSaleComplexNumber={lgeo}"
            )
        elif search_type == "complex":
            return (
                "https://m.land.naver.com/complex/info/"
                f"{var.get('complex_id')}"
                f"?tradTpCd={var.get('trade_type')}"
                f"&ptpNo=&bildNo=&articleListYN=Y"
            )

    def _get_html_element(
        self, search_type: str, method: By, matching_element: str, **kwargs
    ) -> str:
        url = self._make_url(search_type, **kwargs)
        self.driver.get(url)
        html = self.driver.find_element(method, matching_element)
        return html.get_attribute("innerHTML")

    def _search(self, keyword: str) -> Dict:
        info = self._get_html_element(
            "dong", By.XPATH, "//*[@id='mapSearch']/script", keyword=keyword
        )

        # filter, lat, lon 값을 추출하는 정규식 패턴
        pattern = r"filter:\s*({[^}]+})"
        matches = re.search(pattern, info)

        if matches:
            filter_value = matches.group(1)
            filter_dict = {}
            pairs = re.findall(r"(\w+)\s*:\s*'([^']*)'", filter_value)
            for key, value in pairs:
                filter_dict[key] = value
        else:
            print("해당 패턴을 찾을 수 없습니다.")
        return filter_dict

    def get_complex_info(self, keyword: str) -> List[Dict]:
        filter_dict = self._search(keyword)
        info = self._get_html_element(
            "cluster_group", By.XPATH, "/html/body/pre", **filter_dict
        )
        complex_group_list = json.loads(info).get("data").get("COMPLEX")

        # 큰 원으로 구성되어 있는 전체 매물 그룹(complex_list)을 load 하여 한 그룹씩 세부 쿼리 진행
        item_list = []
        for complex in complex_group_list:
            info = self._get_html_element(
                "cluster", By.XPATH, "/html/body/pre", **filter_dict, **complex
            )
            item_list.extend([d for d in json.loads(info).get("result")])
        return item_list

    def get_available_apt(self, complex_id, trade_type="B1"):
        # trade_type은 추후 필요시 추가 - 매매:A1, 전세:B1, 월세: B2, 매매전세:A1:B1
        html = self._get_html_element(
            "complex",
            By.CLASS_NAME,
            "article_box.article_box--sale._article",
            complex_id=complex_id,
            trade_type=trade_type,
        )
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all("div", {"class": "item_inner"})

        if len(items) == 0:
            logging.info(f"complex_id: {complex_id} 네이버 부동산 연결 실패")
            slackbot.warning(f"complex_id: {complex_id} 네이버 부동산 연결에 실패했습니다.")

        item_list = []
        if items:
            for item in items:
                item_id = item.select_one("div > a")["href"].split("/")[-1]
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
                        describe = ""
                    else:
                        describe = detail.text

                item_list.append(
                    {
                        "complex_id": complex_id,
                        "item_id": item_id,
                        "title": title,
                        "building": building,
                        "type": type,
                        "price": price,
                        "size": size,
                        "floor": floor,
                        "direction": direction,
                        "describe": describe,
                    }
                )
        return item_list
