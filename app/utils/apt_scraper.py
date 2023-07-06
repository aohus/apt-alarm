from fastapi import HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import requests

import datetime
import re, math, json
import logging
from typing import List, Dict, Optional

from . import slackbot, report


class NaverAPTScraper:
    def __init__(self):
        self.driver = self._set_chrome_driver()

    def _set_chrome_driver(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("headless")
        # chrome_options.add_argument("--no-sandbox")
        # driver = webdriver.Chrome(options=chrome_options)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )
        logging.info(
            f"[NaverAPTScraper._set_chrome_driver] setting chrome driver success"
        )
        return driver

    def _make_url(self, search_target: str, **kwargs):
        var = kwargs
        if search_target == "dong":
            return f"https://m.land.naver.com/search/result/{var.get('keyword')}"
        elif search_target == "cluster_group":
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
        elif search_target == "cluster":
            cortarNo = var.get("cortarNo")
            z = var.get("z")
            lgeo = var.get("lgeo")
            lat2 = var.get("lat")
            lon2 = var.get("lon")

            lat_margin = 0.118
            lon_margin = 0.111
            btm = float(lat2) - lat_margin
            lft = float(lon2) - lon_margin
            top = float(lat2) + lat_margin
            rgt = float(lon2) + lon_margin

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

    def _get_html_element(
        self, search_target: str, method: By, matching_element: str, **kwargs
    ) -> str:
        url = self._make_url(search_target, **kwargs)
        try:
            self.driver.get(url)
            html = self.driver.find_element(method, matching_element).get_attribute(
                "innerHTML"
            )
            return html
        except Exception as e:
            report.report_error(
                f"주어진 페이지에서 원하는 정보를 찾지 못했습니다. \n search_target: {search_target}, url: {url}",
                str(e),
            )
            raise HTTPException(
                status_code=400,
                detail=f"주어진 페이지에서 원하는 정보를 찾지 못했습니다. 'ㅇㅇ구 ㅇㅇ동' 형식으로 정확히 지역 이름을 입력해주세요.",
            )

    def _get_location_info(self, keyword: str) -> Dict:
        info = self._get_html_element(
            "dong", By.XPATH, "//*[@id='mapSearch']/script", keyword=keyword
        )

        # filter, lat, lon 값을 추출하는 정규식 패턴
        pattern = r"filter:\s*({[^}]+})"
        matches = re.search(pattern, info)

        filter_value = matches.group(1)
        locations = {}
        pairs = re.findall(r"(\w+)\s*:\s*'([^']*)'", filter_value)
        for key, value in pairs:
            locations[key] = value
        return locations

    def get_complex_info(self, keyword: str) -> List[Dict]:
        locations = self._get_location_info(keyword)
        info = self._get_html_element(
            "cluster_group", By.XPATH, "/html/body/pre", **locations
        )
        complex_group_list = json.loads(info).get("data").get("COMPLEX")

        # 큰 원으로 구성되어 있는 전체 매물 그룹(complex_list)을 load 하여 한 그룹씩 세부 쿼리 진행
        item_list = []
        for complex in complex_group_list:
            complex["cortarNo"] = locations["cortarNo"]
            complex["z"] = locations["z"]
            info = self._get_html_element(
                "cluster", By.XPATH, "/html/body/pre", **complex
            )
            item_list.extend([d for d in json.loads(info).get("result")])
        logging.info(
            f"[NaverAPTScraper.get_complex_info] item_list_len:{len(item_list)}"
        )
        return item_list

    @staticmethod
    async def get_available_apt(complex_id, trade_type="B1"):
        URL = "https://m.land.naver.com/complex/getComplexArticleList"
        param = {
            "hscpNo": f"{complex_id}",
            "tradTpCd": f"{trade_type}",
            "order": "point_",
            "showR0": "N",
        }

        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://m.land.naver.com/",
        }

        page = 0
        while True:
            page += 1
            param["page"] = page

            resp = requests.get(URL, params=param, headers=header)
            if resp.status_code != 200:
                report.report_error(f"invalid status: {resp.status_code}")
                break

            data = json.loads(resp.text)
            result = data["result"]

            if result is None:
                logging.error("no result")
                break

            if len(result["list"]) == 0:
                break

            item_list = []
            for item in result["list"]:
                item_info = {
                    "complex_id": complex_id,
                    "complex_name": item.get("atclNm", ""),
                    "item_id": item.get("atclNo", ""),
                    "title": item.get("atclNm", ""),
                    "building": item.get("bildNm", ""),
                    "type": item.get("tradTpNm", ""),
                    "price": item.get("prcInfo"),
                    "size": f"{item.get('spc1')} / {item.get('spc2')}",
                    "floor": item.get("flrInfo", ""),
                    "direction": item.get("direction", ""),
                    "describe": item.get("atclFetrDesc", ""),
                }
                item_list.append(item_info)
                print(item_info)
            logging.info(
                f"[NaverAPTScraper.get_available_apt] item_list_len: {len(item_list)}"
            )
            return item_list

            if result["moreDataYn"] == "N":
                break
        return
