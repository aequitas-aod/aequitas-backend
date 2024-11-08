from typing import Optional, FrozenSet

from pydantic import field_serializer

from domain.common.core import EntityId, Question
from domain.graph.core.enum import Action


class GraphQuestion(Question):

    enabled_by: FrozenSet[EntityId]
    action_needed: Optional[Action]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @field_serializer("enabled_by", when_used="json")
    def serialize_enabled_by_in_order(self, answer_ids: FrozenSet[EntityId]):
        return sorted(answer_ids, key=lambda answer_id: answer_id.code)

    def __str__(self) -> str:
        return (
            f"Question(\n id={self.id},\n text='{self.text}',\n type={self.type},\n "
            f"answers={self.answers},\n enabled_by={self.enabled_by},\n "
            f"action_needed={self.action_needed},\n created_at={self.created_at}\n)"
        )

    def __hash__(self):
        return hash(
            (
                self.id,
                self.text,
                self.type,
                self.answers,
                self.enabled_by,
                self.action_needed,
                self.created_at,
            )
        )
