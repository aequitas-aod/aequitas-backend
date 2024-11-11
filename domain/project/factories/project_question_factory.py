from datetime import datetime
from typing import FrozenSet, List, Optional

from domain.common.core import EntityId
from domain.common.core.enum import QuestionType
from domain.graph.core import GraphQuestion
from domain.project.core import (
    ProjectQuestion,
    ProjectAnswer,
)
from domain.project.core.selection import (
    MultipleSelectionStrategy,
    SingleSelectionStrategy,
)
from domain.project.factories import ProjectAnswerFactory


class ProjectQuestionFactory:

    @staticmethod
    def id_of(code: str, project_id: EntityId) -> EntityId:
        return EntityId(code=code, project_code=project_id.code)

    @staticmethod
    def create_project_question(
        question_id: EntityId,
        text: str,
        question_type: QuestionType,
        answers: FrozenSet[ProjectAnswer],
        created_at: datetime = datetime.now(),
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
        )

    @staticmethod
    def create_project_boolean_question(
        project_question_id: EntityId,
        text: str,
        created_at: datetime = datetime.now(),
    ) -> ProjectQuestion:
        answers: FrozenSet[ProjectAnswer] = frozenset(
            {
                ProjectAnswerFactory.create_project_answer(
                    ProjectAnswerFactory.id_of(
                        code=f"true", project_question_id=project_question_id
                    ),
                    "Yes",
                ),
                ProjectAnswerFactory.create_project_answer(
                    ProjectAnswerFactory.id_of(
                        code=f"false", project_question_id=project_question_id
                    ),
                    "No",
                ),
            }
        )
        return ProjectQuestionFactory.create_project_question(
            project_question_id,
            text,
            QuestionType.BOOLEAN,
            answers,
            created_at,
        )

    @staticmethod
    def from_graph_question(
        graph_question: GraphQuestion,
        project_id: EntityId,
    ) -> ProjectQuestion:
        project_answers: List[ProjectAnswer] = []
        project_question_id: EntityId = ProjectQuestionFactory.id_of(
            graph_question.id.code, project_id
        )
        for a in graph_question.answers:
            project_answer_id: EntityId = ProjectAnswerFactory.id_of(
                a.id.code, project_question_id
            )
            project_answers.append(
                ProjectAnswerFactory.create_project_answer(
                    project_answer_id,
                    a.text,
                    a.description,
                    False,
                )
            )
        return ProjectQuestionFactory.create_project_question(
            project_question_id,
            graph_question.text,
            graph_question.type,
            frozenset(project_answers),
        )
