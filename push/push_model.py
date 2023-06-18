from odmantic import Model, EmbeddedModel
from typing import Optional, List, Union


class NoticedAptModel(Model):
    complex_id: int
    noticed_apt_ids: List[int]

    class Config:
        collection = "noticed_apt"
