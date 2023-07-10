from fastapi import FastAPI, Request
from utils.apt_scraper import NaverAPTScraper
from configs.config import BASE_DIR

from database import mongodb
import re
import logging
from datetime import datetime

from .complex_model import ComplexModel


class ComplexController:
    async def _create_complex(self, complex_list):
        complex_model_list = []
        for complex in complex_list:
            complex_model_list.append(
                ComplexModel(
                    complex_id=complex.get("complex_id"),
                    complex_name=complex.get("complex_name"),
                )
            )
        await mongodb.engine.save_all(complex_model_list)  # 각 모델 인스턴스를 DB에 저장한다.
        return

    async def search_complex(self, request: Request):
        keyword = request.query_params.get("q")  # 쿼리에서 키워드 추출
        if not keyword:  # 키워드가 없다면 사용자에게 검색을 요구
            context = {"request": request}
            return "no input keyword"

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
                    "lease_count": int(complex["leaseCnt"]),
                    "min_lease_price": regex(complex, "leasePrcMin"),
                    "max_lease_price": regex(complex, "leasePrcMax"),
                    # "total_dong_count": complex["totDongCnt"],
                    # "total_apt_count": int(complex["totHsehCnt"]),
                    # "approved_date": complex["useAprvYmd"],
                    # "deal_count": int(complex["dealCnt"]),
                    # "min_space": float(complex["minSpc"]),
                    # "max_space": float(complex["maxSpc"]),
                    # "min_deal_price": regex(complex, "dealPrcMin"),
                    # "max_deal_price": regex(complex, "dealPrcMax"),
                }
            )
        # self._create_complex(regular_complex_list)
        return regular_complex_list
