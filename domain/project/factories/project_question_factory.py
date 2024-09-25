from datetime import datetime
from typing import FrozenSet, List, Optional

from domain.common.core import Answer, AnswerId, QuestionId
from domain.common.core.enum import QuestionType
from domain.common.factories import AnswerFactory
from domain.graph.core import GraphQuestion
from domain.project.core import ProjectQuestion, ProjectAnswer, ProjectId
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
        project_id: ProjectId,
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
            project_id=project_id,
            created_at=created_at,
            selection_strategy=selection_strategy,
            previous_question_id=previous_question_id,
        )

    @staticmethod
    def create_project_boolean_question(
        question_id: QuestionId,
        text: str,
        project_id: ProjectId,
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
            project_id,
            created_at,
            previous_question_id=previous_question_id,
        )

    @staticmethod
    def from_graph_question(
        graph_question: GraphQuestion,
        project_id: ProjectId,
        previous_question_id: Optional[QuestionId],
    ) -> ProjectQuestion:
        project_answers: List[ProjectAnswer] = []
        for a in graph_question.answers:
            project_answers.append(
                ProjectAnswerFactory.create_project_answer(
                    AnswerId(code=f"{project_id.code}-{a.id.code}"),
                    a.text,
                    False,
                )
            )
        return ProjectQuestionFactory.create_project_question(
            QuestionId(code=f"{project_id.code}-{graph_question.id.code}"),
            graph_question.text,
            graph_question.type,
            frozenset(project_answers),
            project_id,
            previous_question_id=previous_question_id,
        )
