import unittest
from datetime import datetime

from domain.common.core import EntityId
from domain.common.core.enum import QuestionType
from domain.project.core import ProjectQuestion
from domain.project.factories import ProjectQuestionFactory, ProjectAnswerFactory, ProjectFactory
from presentation.presentation import deserialize, serialize


class TestProjectQuestionPresentation(unittest.TestCase):

    def setUp(self):
        project_id: EntityId = ProjectFactory.id_of(code="project_id")
        project_question_id: EntityId = ProjectQuestionFactory.id_of(
            code="project_question_id", project_id=project_id
        )
        self.previous_question_id: EntityId = ProjectQuestionFactory.id_of(
            code="project_question_id_2", project_id=project_id
        )
        self.question_timestamp = datetime.now()
        self.question: ProjectQuestion = ProjectQuestionFactory.create_project_question(
            project_question_id,
            "Do you practice TDD?",
            QuestionType.SINGLE_CHOICE,
            frozenset(
                {
                    ProjectAnswerFactory.create_project_answer(
                        ProjectAnswerFactory.id_of(
                            code="false", project_question_id=project_question_id
                        ),
                        "No",
                    ),
                    ProjectAnswerFactory.create_project_answer(
                        ProjectAnswerFactory.id_of(
                            code="true", project_question_id=project_question_id
                        ),
                        "Yes",
                        selected=True,
                    ),
                }
            ),
            created_at=self.question_timestamp,
            previous_question_id=self.previous_question_id,
        )
        self.question_dict: dict = {
            "id": {"code": "project_question_id", "project_code": "project_id"},
            "text": "Do you practice TDD?",
            "type": QuestionType.SINGLE_CHOICE.value,
            "answers": [
                {
                    "id": {
                        "code": "false",
                        "question_code": "project_question_id",
                        "project_code": "project_id",
                    },
                    "text": "No",
                    "description": None,
                    "selected": False,
                },
                {
                    "id": {
                        "code": "true",
                        "question_code": "project_question_id",
                        "project_code": "project_id",
                    },
                    "text": "Yes",
                    "description": None,
                    "selected": True,
                },
            ],
            "created_at": self.question_timestamp.isoformat(),
            "selection_strategy": {"type": "SingleSelectionStrategy"},
            "previous_question_id": {
                "code": "project_question_id_2",
                "project_code": "project_id",
            },
        }

    def test_deserialize_project_question(self):
        actual: ProjectQuestion = deserialize(self.question_dict, ProjectQuestion)
        self.assertEqual(
            self.question,
            actual,
        )

    def test_serialize_project_question(self):
        actual: dict = serialize(self.question)
        self.assertEqual(
            self.question_dict,
            actual,
        )
