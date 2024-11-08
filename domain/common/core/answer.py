from typing import Optional

from pydantic import BaseModel

from domain.common.core import EntityId


class Answer(BaseModel):
    id: EntityId
    text: str
    description: Optional[str]

    def __str__(self):
        return f"Answer(\n id={self.id},\n text='{self.text}',\n description='{self.description}'\n)"

    def __hash__(self):
        return hash((self.id, self.text, self.description))
