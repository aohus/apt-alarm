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


def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    return driver


driver = set_chrome_driver()
url = "https://m.land.naver.com/search/result/이의동"


# 검색 화면
driver.get(url)
info = driver.find_element(By.XPATH, "//*[@id='mapSearch']/script").get_attribute(
    "innerHTML"
)

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

cortarNo = filter_dict.get("cortarNo", None)
z = filter_dict.get("z", None)
lat = filter_dict.get("lat", None)
lon = filter_dict.get("lon", None)

# 재구성
lat_margin = 0.118
lon_margin = 0.111

btm = float(lat) - lat_margin
lft = float(lon) - lon_margin
top = float(lat) + lat_margin
rgt = float(lon) + lon_margin

# 최초 요청 시 디폴트 값으로 설정되어 있으나, 원하는 값으로 구성
rletTpCd = "APT"  # 아파트
tradTpCd = "A1:B1"  # 매매/전세/월세 매물 확인

# 매물 정보 요청
driver.implicitly_wait(5)
remaked_url = f"https://m.land.naver.com/cluster/clusterList?view=atcl&cortarNo={cortarNo}&rletTpCd={rletTpCd}&tradTpCd={tradTpCd}&z={z}&lat={lat}&lon={lon}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&addon=COMPLEX&isOnlyIsale=false"
driver.get(remaked_url)
info = driver.find_element(By.XPATH, "/html/body/pre")
values = json.loads(info.get_attribute("innerHTML")).get("data").get("COMPLEX")


# 큰 원으로 구성되어 있는 전체 매물그룹(values)을 load 하여 한 그룹씩 세부 쿼리 진행
for v in values:
    lgeo = v["lgeo"]
    count = v["count"]
    lat2 = v["lat"]
    lon2 = v["lon"]
    # if count > 1:
    remaked_url2 = f"https://m.land.naver.com/cluster/ajax/complexList?itemId={lgeo}&mapKey=&lgeo={lgeo}&rletTpCd={rletTpCd}&tradTpCd={tradTpCd}&z={z}&lat={lat2}&lon={lon2}&btm={btm}&lft={lft}&top={top}&rgt={rgt}&cortarNo={cortarNo}&isOnlyIsale=false&poiType=CC&preSaleComplexNumber={lgeo}"
    driver.get(remaked_url2)
    info = driver.find_element(By.XPATH, "/html/body/pre")
    values = json.loads(info.get_attribute("innerHTML"))
    print(values)
