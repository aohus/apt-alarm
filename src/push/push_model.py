from odmantic import Model, EmbeddedModel
from typing import Optional, List, Union


class NoticedAptModel(Model):
    user_id: str
    noticed_apt_ids: List[str]

    class Config:
        collection = "noticed_apt"
