from abc import ABC
from datetime import datetime
from typing import FrozenSet

from pydantic import BaseModel, field_serializer

from domain.common.core import Answer, EntityId
from domain.common.core.enum import QuestionType


class Question(ABC, BaseModel):
    id: EntityId
    text: str
    type: QuestionType
    answers: FrozenSet[Answer]
    created_at: datetime

    @field_serializer("answers", when_used="json")
    def serialize_answers_in_order(self, answers: FrozenSet[Answer]):
        return sorted(answers, key=lambda answer: answer.text)

    def __str__(self) -> str:
        return (
            f"Question(\n id={self.id},\n text='{self.text}',\n type={self.type},\n"
            f" answers={self.answers},\n created_at={self.created_at}\n)"
        )

    def __hash__(self):
        return hash(
            (
                self.id,
                self.text,
                self.type,
                self.answers,
                self.created_at,
            )
        )
