from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing_extensions import FrozenSet

from domain.common.core import AnswerId
from domain.project.core.project_answer import ProjectAnswer


class SelectionStrategy(ABC, BaseModel):

    @abstractmethod
    def select_answer(
        self, answer_id: AnswerId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        """
        Selects an answer from a set of answers.
        :param answer_id: The answer to select.
        :param answers: The set of answers.
        :return: The new set of answers containing the answer selected.
        :raises ValueError: If the answer is not in the set of answers.
        """
        pass

    @abstractmethod
    def deselect_answer(
        self, answer_id: AnswerId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        """
        Deselects an answer from a set of answers.
        :param answer_id: The answer to deselect.
        :param answers: The set of answers.
        :return: The new set of answers containing the answer deselected.
        :raises ValueError: If the answer is not in the set of answers.
        """
        pass

    def _check_answer_exists(
        self, answer_id: AnswerId, answers: FrozenSet[ProjectAnswer]
    ) -> None:
        if not any(answer.id == answer_id for answer in answers):
            raise ValueError(f"Answer {answer_id} is not available for this question")
