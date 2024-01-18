import json
import logging
import os
import threading
from typing import Dict
from typing import List

import httpx
from bs4 import BeautifulSoup


class URLBuilder:
    HOST_URL = "https://new.land.naver.com"
    MOBILE_URL = "https://m.land.naver.com"

    @classmethod
    def make_search_complex_url(cls, path):
        return cls.HOST_URL + path

    @classmethod
    def make_complex_detail_url(cls, cortarNo, leftLon, rightLon, topLat, bottomLat):
        path = (
            "/api/complexes/single-markers/2.0"
            f"?cortarNo={cortarNo}&zoom=16&priceType=RETAIL&markerId"
            "&markerType&selectedComplexNo&selectedComplexBuildingNo"
            "&fakeComplexMarker&realEstateType=APT%3AABYG%3AJGC%3APRE"
            "&tradeType=B1&tag=%3A%3A%3A%3A%3A%3A%3A%3A&rentPriceMin=0"
            "&rentPriceMax=900000000&priceMin=0&priceMax=900000000&areaMin=0&areaMax=900000000"
            "&oldBuildYears&recentlyBuildYears&minHouseHoldCount&maxHouseHoldCount"
            "&showArticle=false&sameAddressGroup=true&minMaintenanceCost&maxMaintenanceCost&directions="
            f"&leftLon={leftLon}&rightLon={rightLon}&topLat={topLat}&bottomLat={bottomLat}"
            "&isPresale=true"
        )
        return cls.HOST_URL + path


class RequestTransporter:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://new.land.naver.com/",
        }

    async def requests(self, url, params=None):
        try:
            async with httpx.AsyncClient(timeout=60, follow_redirects=True) as client:
                res = await client.get(url, params=params, headers=self.headers)
                # res.raise_for_status()
                try:
                    return json.loads(res.text)
                except json.JSONDecodeError:
                    return res.text
        except httpx.RequestException as e:
            raise SystemExit(e)
        except Exception as e:
            raise e


class APTDataParser:
    def __init__(self):
        self.request_transporter = RequestTransporter()

    async def parse(self, data, keyword):
        # tmp
        if not data.get("isShown"):
            return []

        if "regions" in data:  # 같은 지역명 여러개 일 때
            return [
                {
                    "markerId": "103072",
                    "complexName": "지역명 여러개임 바꿀 예정",
                    "totalDongCount": 4,
                    "minLeasePrice": 60000,
                    "maxLeasePrice": 65000,
                    "leaseCount": 2,
                }
            ]
        if "locations" in data:  # 지역이 애매할 때
            return [
                {
                    "markerId": "103072",
                    "complexName": "지역명 여러개임 바꿀 예정",
                    "totalDongCount": 4,
                    "minLeasePrice": 60000,
                    "maxLeasePrice": 65000,
                    "leaseCount": 2,
                }
            ]

        if "deepLink" in data:
            item_list = await self.final(keyword)
            return item_list

    @staticmethod
    def _get_boundary(lat, lon):
        lat_margin = 0.0066
        lon_margin = 0.013
        return (
            float(lon) - lon_margin,
            float(lon) + lon_margin,
            float(lat) + lat_margin,
            float(lat) - lat_margin,
        )

    async def final(self, keyword):
        search_result_html = await self._fetch_search_result_html(keyword)
        lat, lon, cortarNo = self._parse_search_result_html(search_result_html)

        leftLon, rightLon, topLat, bottomLat = self._get_boundary(lat, lon)
        cortar_url = URLBuilder.make_complex_detail_url(
            cortarNo, leftLon, rightLon, topLat, bottomLat
        )
        detail_data = await self._fetch_detail_data(cortar_url)
        return detail_data

    async def _fetch_search_result_html(self, keyword):
        url = "https://m.land.naver.com/search/result/{}".format(keyword)
        res = await self.request_transporter.requests(url)
        return res

    def _parse_search_result_html(self, html):
        soup = (str)(BeautifulSoup(html, "lxml"))
        value = (
            soup.split("filter: {")[1].split("}")[0].replace(" ", "").replace("'", "")
        )

        lat = value.split("lat:")[1].split(",")[0]
        lon = value.split("lon:")[1].split(",")[0]
        cortarNo = value.split("cortarNo:")[1].split(",")[0]
        return lat, lon, cortarNo

    async def _fetch_detail_data(self, url):
        res = await self.request_transporter.requests(url)
        return res


class NaverAPTScraper:
    def __init__(self):
        self.parser = APTDataParser()
        self.request_transporter = RequestTransporter()

    async def get_complex_info(self, keyword: str) -> List[Dict]:
        params = {"keyword": keyword}
        url = URLBuilder.make_search_complex_url("/api/search")
        data = await self.request_transporter.requests(url, params)
        item_list = await self.parser.parse(data, keyword)

        logging.info(
            f"{keyword}, processId: {os.getpid()}, threadID: {threading.get_ident()}"
        )

        return item_list
