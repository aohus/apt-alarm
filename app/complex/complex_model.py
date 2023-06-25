from odmantic import Model, EmbeddedModel
from typing import Optional, List, Union


class ComplexModel(Model):
    complex_id: int
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
