from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, ORJSONResponse
from fastapi.templating import Jinja2Templates
from apt_scraper import NaverAPTScraper
from configs.config import BASE_DIR

from database import mongodb
import re
import logging
from datetime import datetime

from models.model import ComplexModel, InterestModel, NoticedAptModel, Conditions


app = FastAPI(title="부동산 정보", version="0.0.1")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    context = {"request": request, "title": "부동산 정보"}
    return templates.TemplateResponse("main.html", context=context)


@app.get("/search", response_class=HTMLResponse)
def search_result(request: Request):
    keyword = request.query_params.get("q")  # 쿼리에서 키워드 추출
    if not keyword:  # 키워드가 없다면 사용자에게 검색을 요구
        context = {"request": request}
        return templates.TemplateResponse("main.html", context=context)

    def regex(item, keyword):
        value = item.get(keyword)
        if value:
            if value[-1] == ";":
                return int(re.sub(r"\D", "", value) + "00000000") / 100000000
            else:
                return int(re.sub(r"\D", "", value) + "0000") / 100000000
        else:
            return None

    naver_apt_scraper = NaverAPTScraper()  # 수집기 인스턴스
    complex_list = naver_apt_scraper.get_complex_info(keyword)  # 데이터 수집
    logging.info(
        f"[{datetime.now}] '{keyword}' length of complex list :{len(complex_list)}"
    )
    # complex_models = []
    regular_complex_list = []
    for complex in complex_list:
        regular_complex_list.append(
            {
                "complex_id": int(complex["hscpNo"]),
                "complex_name": complex["hscpNm"],
                "total_dong_count": complex["totDongCnt"],
                "total_apt_count": int(complex["totHsehCnt"]),
                "approved_date": complex["useAprvYmd"],
                "deal_count": int(complex["dealCnt"]),
                "lease_count": int(complex["leaseCnt"]),
                "min_space": float(complex["minSpc"]),
                "max_space": float(complex["maxSpc"]),
                "min_deal_price": regex(complex, "dealPrcMin"),
                "max_deal_price": regex(complex, "dealPrcMax"),
                "min_lease_price": regex(complex, "leasePrcMin"),
                "max_lease_price": regex(complex, "leasePrcMax"),
            }
        )
    return templates.TemplateResponse(
        "main.html", context={"request": request, "complexes": regular_complex_list}
    )


@app.get("/interest", response_class=HTMLResponse)
async def get_interest_complex_list(request: Request):
    if not "회원":
        return  # TODO: 로그인/회원가입 화면

    if await mongodb.engine.find_one(
        InterestModel, InterestModel.user_id == 1
    ):  # TODO: 로그인 만들기
        # 키워드에 대해 수집된 데이터가 DB에 존재한다면 해당 데이터를 사용자에게 보여준다.
        complex_list = await mongodb.engine.find(
            InterestModel, InterestModel.user_id == 1
        )
        context = {"request": request, "user_id": 1, "complex_list": complex_list}
        return templates.TemplateResponse("main.html", context=context)  # TODO: MYPAGE
    else:
        return templates.TemplateResponse(
            "main.html", context=context
        )  # 알림 요청한 아파트 단지가 없습니다.


@app.post("/interest/{complex_id}")
async def add_interest_complex(complex_id: int, complex: ComplexModel):
    print(complex.complex_name)
    interest_model = InterestModel(
        user_id="1",
        complex_id=complex_id,
        complex_name=complex.complex_name,
        conditions=Conditions(min_size=10, min_floors=1, max_floors=10, price=4),
    )
    await mongodb.engine.save(interest_model)  # 각 모델 인스턴스를 DB에 저장한다.
    return complex


@app.patch("/interest/{complex_id}", response_class=HTMLResponse)
async def patch_interest_complex(complex_id: int, request: Request):
    data = request.complex_id
    # TODO : user_id, complex_id 같은 것 있으면 지우고 추가, 뒤집어 쓰기
    interest_model = InterestModel(
        user_id=1,
        complex_id=complex_id,
        complex_name=data.get("complex_name"),
    )
    await mongodb.engine.save(interest_model)
    return


@app.delete("/interest/{complex_id}", response_class=HTMLResponse)
async def delete_interest_complex(complex_id: int, request: Request):
    await mongodb.engine.delete(
        InterestModel,
        (InterestModel.user_id == 1) & (InterestModel.complex_id == complex_id),
    )


@app.on_event("startup")
async def on_app_start():
    """
    before app starts
    """
    mongodb.connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    """
    after app shutdown
    """
    mongodb.close()
