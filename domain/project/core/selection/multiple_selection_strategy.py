from typing_extensions import FrozenSet

from domain.common.core import EntityId
from domain.project.core import ProjectAnswer
from domain.project.core.selection import SelectionStrategy


class MultipleSelectionStrategy(SelectionStrategy):
    """
    Strategy to select and deselect answers for multiple choice questions.
    """

    def select_answer(
        self, answer_id: EntityId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        if not self._answer_exists(answer_id, answers):
            raise ValueError(f"Answer {answer_id} is not available for this question")
        answer = list(filter(lambda a: a.id == answer_id, answers))[0]
        return answers.difference({answer}).union({answer.select()})

    def deselect_answer(
        self, answer_id: EntityId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        if not self._answer_exists(answer_id, answers):
            raise ValueError(f"Answer {answer_id} is not available for this question")
        answer = list(filter(lambda a: a.id == answer_id, answers))[0]
        return answers.difference({answer}).union({answer.deselect()})

    def __str__(self):
        return "MultipleSelectionStrategy"
