from odmantic import Model
from typing import Optional


class ComplexModel(Model):
    item_id: int
    type: str
    apt_name: str
    total_dong_count: int
    total_apt_count: int
    approve_date: str
    deal_count: int
    lease_count: int
    min_space: float
    max_space: float
    min_deal_price: Optional[int]
    max_deal_price: Optional[int]
    min_lease_price: Optional[int]
    max_lease_price: Optional[int]

    class Config:
        collection = "complex"


class AptModel(Model):
    item_id: int
    apt_name: str
    total_dong_count: int
    total_apt_count: int
    approve_date: str
    deal_count: int
    lease_count: int
    min_space: int
    max_space: int
    min_deal_price: int
    max_deal_price: int
    min_lease_price: int
    max_lease_price: int

    class Config:
        collection = "apt"
