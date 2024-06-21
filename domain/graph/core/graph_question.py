from typing import Optional, FrozenSet

from pydantic import BaseModel, field_serializer

from domain.common.core import AnswerId, Question
from domain.graph.core.enum import Action


class GraphQuestion(Question, BaseModel):

    enabled_by: FrozenSet[AnswerId]
    action_needed: Optional[Action]

    @field_serializer("enabled_by", when_used="json")
    def serialize_enabled_by_in_order(self, answer_ids: FrozenSet[AnswerId]):
        return sorted(answer_ids, key=lambda answer_id: answer_id.code)

    def __str__(self) -> str:
        return (
            f"Question(\n id={self.id},\n text='{self.text}',\n type={self.type}, \n"
            f"available_answers={self.available_answers},\n enabled_by={self.enabled_by},\n "
            f"action_needed={self.action_needed}, created_at={self.created_at}\n)"
        )

    def __hash__(self):
        return hash(
            (
                self.id.code,
                self.text,
                self.type,
                self.available_answers,
                self.enabled_by,
                self.action_needed,
                self.created_at,
            )
        )
