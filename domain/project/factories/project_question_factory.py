from datetime import datetime
from typing import FrozenSet

from domain.common.core import Answer, AnswerId, QuestionId
from domain.common.core.enum import QuestionType
from domain.common.factories import AnswerFactory
from domain.project.core import ProjectQuestion, ProjectAnswer
from domain.project.core.selection import (
    MultipleSelectionStrategy,
    SingleSelectionStrategy,
)
from domain.project.factories import ProjectAnswerFactory


class ProjectQuestionFactory:

    @staticmethod
    def create_project_question(
        question_id: QuestionId,
        text: str,
        question_type: QuestionType,
        answers: FrozenSet[ProjectAnswer],
        created_at: datetime = datetime.now(),
        previous_question_id: QuestionId = None,
    ) -> ProjectQuestion:
        match question_type:
            case QuestionType.BOOLEAN:
                selection_strategy = SingleSelectionStrategy()
            case QuestionType.SINGLE_CHOICE:
                selection_strategy = SingleSelectionStrategy()
            case QuestionType.MULTIPLE_CHOICE:
                selection_strategy = MultipleSelectionStrategy()
            case QuestionType.RATING:
                selection_strategy = SingleSelectionStrategy()
            case _:
                raise ValueError(f"Unsupported question type {question_type}")

        selected_answers = list(filter(lambda answer: answer.selected, answers))
        if len(selected_answers) > 1 and question_type != QuestionType.MULTIPLE_CHOICE:
            raise ValueError(
                "Selected answers are only allowed for multiple choice questions"
            )
        return ProjectQuestion(
            id=question_id,
            text=text,
            type=question_type,
            answers=answers,
            created_at=created_at,
            selection_strategy=selection_strategy,
            previous_question_id=previous_question_id,
        )

    @staticmethod
    def create_project_boolean_question(
        question_id: QuestionId,
        text: str,
        created_at: datetime = datetime.now(),
        previous_question_id: QuestionId = None,
    ) -> ProjectQuestion:
        answers: FrozenSet[ProjectAnswer] = frozenset(
            {
                ProjectAnswerFactory.create_project_answer(
                    AnswerId(code=f"{question_id.code}-true"), "Yes"
                ),
                ProjectAnswerFactory.create_project_answer(
                    AnswerId(code=f"{question_id.code}-false"), "No"
                ),
            }
        )
        return ProjectQuestionFactory.create_project_question(
            question_id,
            text,
            QuestionType.BOOLEAN,
            answers,
            created_at,
            previous_question_id=previous_question_id,
        )