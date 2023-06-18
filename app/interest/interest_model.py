from odmantic import Model, EmbeddedModel
from typing import Optional, List, Union


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
