import json
import logging
from typing import Dict
from typing import List

import requests
from bs4 import BeautifulSoup


class URLBuilder:
    @classmethod
    def make_url(cls, path):
        HOST_URL = "https://new.land.naver.com"
        return HOST_URL + path

    @classmethod
    def make_complex_path(cls, cortarNo, leftLon, rightLon, topLat, bottomLat):
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
        return URLBuilder.make_url(path)


class NaverAPTScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://new.land.naver.com/",
        }

    def get_complex_info(self, keyword: str) -> List[Dict]:
        param = {"keyword": keyword}
        url = URLBuilder.make_url("/api/search")
        try:
            res = requests.get(url, params=param, headers=self.headers)
            data = json.loads(res.text)
        except Exception as e:
            raise e

        item_list = self.parse(data, keyword)
        logging.info(
            f"[NaverAPTScraper.get_complex_info] item_list_len:{len(item_list)}"
        )
        return item_list

    def parse(self, data, keyword):
        # tmp
        if "regions" in data:
            return [
                {
                    "markerId": "103072",
                    "markerType": "COMPLEX",
                    "latitude": 37.304899,
                    "longitude": 127.048914,
                    "complexName": "광교한양수자인",
                    "realEstateTypeCode": "APT",
                    "realEstateTypeName": "아파트",
                    "completionYearMonth": "201107",
                    "totalDongCount": 4,
                    "totalHouseholdCount": 214,
                    "floorAreaRatio": 119,
                    "minDealUnitPrice": 2755,
                    "maxDealUnitPrice": 3673,
                    "minLeaseUnitPrice": 1837,
                    "maxLeaseUnitPrice": 1971,
                    "minLeaseRate": 50,
                    "maxLeaseRate": 69,
                    "minArea": "108.22",
                    "maxArea": "109.26",
                    "minDealPrice": 0,
                    "maxDealPrice": 0,
                    "minLeasePrice": 60000,
                    "maxLeasePrice": 65000,
                    "minRentPrice": 0,
                    "maxRentPrice": 0,
                    "minShortTermRentPrice": 0,
                    "maxShortTermRentPrice": 0,
                    "isLeaseShown": True,
                    "priceCount": 1,
                    "representativeArea": 109.0,
                    "medianDealUnitPrice": 2881,
                    "medianLeaseUnitPrice": 1971,
                    "medianLeaseRate": 68,
                    "medianLeasePrice": 65000,
                    "isPresales": False,
                    "representativePhoto": "/20170822_184/apt_realimage_15033877064238G6hS_JPEG/79657266a48ed1dfa2283c97c1c9d0a0.jpg",
                    "photoCount": 0,
                    "dealCount": 0,
                    "leaseCount": 2,
                    "rentCount": 0,
                    "shortTermRentCount": 0,
                    "totalArticleCount": 2,
                    "existPriceTab": True,
                }
            ]

        if "deepLink" in data:
            item_list = self.final(keyword)
            return item_list

    def get_boundary(self, lat, lon):
        lat_margin = 0.0066
        lon_margin = 0.013
        return (
            float(lon) - lon_margin,
            float(lon) + lon_margin,
            float(lat) + lat_margin,
            float(lat) - lat_margin,
        )

    def final(self, keyword):
        url = "https://m.land.naver.com/search/result/{}".format(keyword)
        res = requests.get(url, headers=self.headers)
        soup = (str)(BeautifulSoup(res.text, "lxml"))
        value = (
            soup.split("filter: {")[1].split("}")[0].replace(" ", "").replace("'", "")
        )

        lat = value.split("lat:")[1].split(",")[0]
        lon = value.split("lon:")[1].split(",")[0]
        cortarNo = value.split("cortarNo:")[1].split(",")[0]

        leftLon, rightLon, topLat, bottomLat = self.get_boundary(lat, lon)
        cortar_url = URLBuilder.make_complex_path(
            cortarNo, leftLon, rightLon, topLat, bottomLat
        )
        res = requests.get(cortar_url, headers=self.headers)
        return json.loads(res.text)
