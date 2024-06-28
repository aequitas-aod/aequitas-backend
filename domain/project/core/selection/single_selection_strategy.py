from typing import Any

from typing_extensions import FrozenSet

from domain.common.core import AnswerId
from domain.project.core import ProjectAnswer
from domain.project.core.selection import SelectionStrategy


class SingleSelectionStrategy(SelectionStrategy):
    """
    A selection strategy that allows selecting only one answer at a time.
    """

    def select_answer(
            self, answer_id: AnswerId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        self._check_answer_exists(answer_id, answers)
        new_answers = set()
        for answer in answers:
            new_answers.add(
                answer.select() if answer.id == answer_id else answer.deselect()
            )
        return frozenset(new_answers)

    def deselect_answer(
            self, answer_id: AnswerId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        self._check_answer_exists(answer_id, answers)
        answer = list(filter(lambda answer: answer.id == answer_id, answers))[0]
        return answers.difference({answer}).union({answer.deselect()})

    def __str__(self):
        return "SingleSelectionStrategy"
