from abc import ABC
from datetime import datetime
from typing import FrozenSet

from pydantic import BaseModel, field_serializer

from domain.common.core import Answer, QuestionId
from domain.common.core.enum import QuestionType


class Question(ABC, BaseModel):
    id: QuestionId
    text: str
    type: QuestionType
    available_answers: FrozenSet[Answer]
    created_at: datetime

    @field_serializer("available_answers", when_used="json")
    def serialize_available_answers_in_order(self, answers: FrozenSet[Answer]):
        return sorted(answers, key=lambda answer: answer.text)

    def __str__(self) -> str:
        return (
            f"Question(\n id={self.id},\n text='{self.text}',\n type={self.type}, \n"
            f"available_answers={self.available_answers}, \n"
            f"created_at={self.created_at}\n)"
        )

    def __hash__(self):
        return hash(
            (
                self.id.code,
                self.text,
                self.type,
                self.available_answers,
                self.created_at,
            )
        )
