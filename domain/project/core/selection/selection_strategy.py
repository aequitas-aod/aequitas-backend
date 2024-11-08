from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing_extensions import FrozenSet

from domain.common.core import EntityId
from domain.project.core import ProjectAnswer


class SelectionStrategy(ABC, BaseModel):

    @abstractmethod
    def select_answer(
        self, answer_id: EntityId, answers: FrozenSet[ProjectAnswer]
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
        self, answer_id: EntityId, answers: FrozenSet[ProjectAnswer]
    ) -> FrozenSet[ProjectAnswer]:
        """
        Deselects an answer from a set of answers.
        :param answer_id: The answer to deselect.
        :param answers: The set of answers.
        :return: The new set of answers containing the answer deselected.
        :raises ValueError: If the answer is not in the set of answers.
        """
        pass

    def _answer_exists(
        self, answer_id: EntityId, answers: FrozenSet[ProjectAnswer]
    ) -> bool:
        """
        Checks if an answer exists in a set of answers.
        """
        return any(answer.id == answer_id for answer in answers)
