from typing import FrozenSet, Any, Optional

from pydantic import field_serializer, field_validator
from typing_extensions import Self

from domain.common.core import Question, EntityId
from domain.project.core import ProjectAnswer
from domain.project.core.selection import (
    SelectionStrategy,
    SingleSelectionStrategy,
    MultipleSelectionStrategy,
)


class ProjectQuestion(Question):
    id: EntityId
    answers: FrozenSet[ProjectAnswer]
    selection_strategy: SelectionStrategy
    previous_question_id: Optional[EntityId]

    def select_answer(self, answer_id: EntityId) -> Self:
        answers: FrozenSet[ProjectAnswer] = self.selection_strategy.select_answer(
            answer_id, self.answers
        )
        return ProjectQuestion(
            id=self.id,
            text=self.text,
            type=self.type,
            answers=answers,
            created_at=self.created_at,
            selection_strategy=self.selection_strategy,
            previous_question_id=self.previous_question_id,
        )

    def deselect_answer(self, answer_id: EntityId) -> Self:
        answers = self.selection_strategy.deselect_answer(answer_id, self.answers)
        return ProjectQuestion(
            id=self.id,
            text=self.text,
            type=self.type,
            answers=answers,
            created_at=self.created_at,
            selection_strategy=self.selection_strategy,
            previous_question_id=self.previous_question_id,
        )

    def deselect_all_answers(self) -> Self:
        new_answers = frozenset(map(lambda a: a.deselect(), self.answers))
        return ProjectQuestion(
            id=self.id,
            text=self.text,
            type=self.type,
            answers=new_answers,
            created_at=self.created_at,
            selection_strategy=self.selection_strategy,
            previous_question_id=self.previous_question_id,
        )

    @field_serializer("selection_strategy", when_used="json")
    def serialize_selection_strategy(self, selection_strategy: SelectionStrategy):
        if isinstance(selection_strategy, SelectionStrategy):
            return {"type": self.selection_strategy.__class__.__name__}
        else:
            raise ValueError(
                f"Unsupported selection strategy {self.selection_strategy}"
            )

    @field_validator("selection_strategy", mode="before")
    def deserialize_selection_strategy(cls, value: Any):
        if isinstance(value, SelectionStrategy):
            return value
        elif isinstance(value, dict) and "type" in value:
            strategy_type = value["type"]
            if strategy_type == "SingleSelectionStrategy":
                return SingleSelectionStrategy()
            elif strategy_type == "MultipleSelectionStrategy":
                return MultipleSelectionStrategy()
            else:
                raise ValueError(f"Unsupported selection strategy type {strategy_type}")
        else:
            raise ValueError("Invalid selection strategy value")

    @field_serializer("answers", when_used="json")
    def serialize_answers_in_order(self, answer_ids: FrozenSet[ProjectAnswer]):
        return sorted(answer_ids, key=lambda answer: answer.id.code)

    def __str__(self) -> str:
        return (
            f"ProjectQuestion(id={self.id},\n text={self.text},\n type={self.type},\n answers={self.answers},\n "
            f"created_at={self.created_at},\n selection_strategy={self.selection_strategy},\n "
            f"previous_question_id={self.previous_question_id}\n)"
        )

    def __hash__(self):
        return hash(
            (
                self.text,
                self.type,
                self.answers,
                self.created_at,
                self.selection_strategy,
                self.previous_question_id,
            )
        )
