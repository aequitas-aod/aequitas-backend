from datetime import datetime
from typing import FrozenSet, Optional

from domain.common.core import Answer, AnswerId, QuestionId
from domain.common.core.enum import QuestionType
from domain.common.factories import AnswerFactory
from domain.graph.core import GraphQuestion
from domain.graph.core.enum import Action


class GraphQuestionFactory:

    @staticmethod
    def create_question(
        question_id: QuestionId,
        text: str,
        question_type: QuestionType,
        answers: FrozenSet[Answer],
        created_at: datetime = datetime.now(),
        enabled_by: FrozenSet[AnswerId] = frozenset(),
        action_needed: Optional[Action] = None,
    ) -> GraphQuestion:
        return GraphQuestion(
            id=question_id,
            text=text,
            type=question_type,
            answers=answers,
            created_at=created_at,
            enabled_by=enabled_by,
            action_needed=action_needed,
        )

    @staticmethod
    def create_boolean_question(
        question_id: QuestionId,
        text: str,
        created_at: datetime = datetime.now(),
        enabled_by: FrozenSet[AnswerId] = frozenset(),
        action_needed: Optional[Action] = None,
    ) -> GraphQuestion:
        answers: FrozenSet[Answer] = frozenset(
            {
                AnswerFactory.create_boolean_answer(
                    AnswerId(code=f"{question_id.code}-true"), True
                ),
                AnswerFactory.create_boolean_answer(
                    AnswerId(code=f"{question_id.code}-false"), False
                ),
            }
        )
        return GraphQuestionFactory.create_question(
            question_id,
            text,
            QuestionType.BOOLEAN,
            answers,
            created_at,
            enabled_by,
            action_needed,
        )
