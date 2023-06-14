from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from apt_scraper import NaverAPTScraper
from configs.config import BASE_DIR
import re
import logging
from datetime import datetime

# from models import mongodb
from models.model import ComplexModel


app = FastAPI(title="부동산 정보", version="0.0.1")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    context = {"request": request, "title": "부동산 정보"}
    return templates.TemplateResponse("index.html", context=context)


@app.get("/search", response_class=HTMLResponse)
def search_result(request: Request):
    keyword = request.query_params.get("q")  # 쿼리에서 키워드 추출
    if not keyword:  # 키워드가 없다면 사용자에게 검색을 요구
        context = {"request": request}
        return templates.TemplateResponse("index.html", context=context)
    # if await mongodb.engine.find_one(ComplexModel, ComplexModel.keyword == keyword):
    #     # 키워드에 대해 수집된 데이터가 DB에 존재한다면 해당 데이터를 사용자에게 보여준다.
    #     books = await mongodb.engine.find(ComplexModel, ComplexModel.keyword == keyword)
    #     context = {"request": request, "keyword": keyword, "books": books}
    #     return templates.TemplateResponse("index.html", context=context)

    def regex(item, keyword):
        value = item.get(keyword)
        if value:
            return int(re.sub(r"\D", "", value))
        else:
            return None

        return value

    naver_apt_scraper = NaverAPTScraper()  # 수집기 인스턴스
    complex_list = naver_apt_scraper.get_complex_info(keyword)  # 데이터 수집
    logging.info(
        f"[{datetime.now}] '{keyword}' length of complex list :{len(complex_list)}"
    )
    complex_models = []
    for item in complex_list:
        complex_model = ComplexModel(
            item_id=int(item["hscpNo"]),
            apt_name=item["hscpNm"],
            type="complex",
            total_dong_count=int(item["totDongCnt"]),
            total_apt_count=int(item["totHsehCnt"]),
            approve_date=item["useAprvYmd"],
            deal_count=int(item["dealCnt"]),
            lease_count=int(item["leaseCnt"]),
            min_space=float(item["minSpc"]),
            max_space=float(item["maxSpc"]),
            min_deal_price=regex(item, "dealPrcMin"),
            max_deal_price=regex(item, "dealPrcMax"),
            min_lease_price=regex(item, "leasePrcMin"),
            max_lease_price=regex(item, "leasePrcMax"),
        )
        complex_models.append(complex_model)
    print(naver_apt_scraper.get_available_apt(608))
    # await mongodb.engine.save_all(complex_models)  # 각 모델 인스턴스를 DB에 저장한다.
    # context = {"request": request, "keyword": keyword, "complex": complex_models}
    # return templates.TemplateResponse("index.html", context=context)
    # print(complex_list)
    return "good"


# @app.on_event("startup")
# async def on_app_start():
#     """
#     before app starts
#     """
#     await mongodb.connect()


# @app.on_event("shutdown")
# async def on_app_shutdown():
#     """
#     after app shutdown
#     """
#     await mongodb.close()
