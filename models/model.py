from odmantic import Model, EmbeddedModel
from typing import Optional, List, Union


class ComplexModel(Model):
    # complex_id: int
    complex_name: str
    # total_dong_count: int
    # total_apt_count: int
    # approved_date: str
    # deal_count: int
    # lease_count: int
    # min_space: float
    # max_space: float
    # min_deal_price: float
    # max_deal_price: float
    # min_lease_price: float
    # max_lease_price: float

    class Config:
        collection = "complex"


class Conditions(EmbeddedModel):
    min_size: float
    min_floors: int
    max_floors: int
    price: float


class InterestModel(Model):  # 이렇게 하는 것이 나을까? 아님, user 하나당 하나의 row만 가지게 하는 것이 좋을까??
    user_id: str
    complex_id: int
    complex_name: str
    conditions: Conditions

    class Config:
        collection = "interest"


class NoticedAptModel(Model):
    complex_id: int
    noticed_apt_ids: List[int]

    class Config:
        collection = "noticed_apt"
