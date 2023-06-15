from odmantic import Model, EmbeddedModel
from typing import Optional, List


class ComplexModel(Model):
    complex_id: int
    complex_name: str
    total_dong_count: int
    total_apt_count: int
    approved_date: str
    deal_count: int
    lease_count: int
    min_space: float
    max_space: float
    min_deal_price: Optional[float]
    max_deal_price: Optional[float]
    min_lease_price: Optional[float]
    max_lease_price: Optional[float]

    # class Config:
    #     collection = "complex"


class Conditions(EmbeddedModel):
    min_size: float
    min_floors: int
    max_floors: int
    price: int


class InterestModel(Model):
    user_id: str
    complex_id: int
    complex_name: str
    conditions: Optional[Conditions]

    class Config:
        collection = "interest"


class NoticedAptModel(Model):
    complex_id: int
    noticed_apt_ids: List[int]

    class Config:
        collection = "noticed_apt"
