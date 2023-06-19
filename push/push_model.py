from odmantic import Model, EmbeddedModel
from typing import Optional, List, Union


class NoticedAptModel(Model):
    user_id: str
    noticed_apt_ids: List[int]

    class Config:
        collection = "noticed_apt"
