import unittest
from datetime import datetime
from select import select
from typing import FrozenSet

from domain.common.core import EntityId
from domain.common.core.enum import QuestionType
from domain.project.core import (
    ProjectQuestion,
    ProjectAnswer,
)
from domain.project.factories import (
    ProjectQuestionFactory,
    ProjectAnswerFactory,
    ProjectFactory,
)


class TestProjectQuestionSingleChoice(unittest.TestCase):

    def setUp(self):
        self.project_id: EntityId = ProjectFactory.id_of(code="project_id")
        self.project_question_id: EntityId = ProjectQuestionFactory.id_of(
            code="question_id", project_id=self.project_id
        )
        self.question_timestamp = datetime.now()
        self.question: ProjectQuestion = ProjectQuestionFactory.create_project_question(
            self.project_question_id,
            "Do you practice TDD?",
            QuestionType.MULTIPLE_CHOICE,
            frozenset(
                {
                    ProjectAnswerFactory.create_project_answer(
                        answer_id=ProjectAnswerFactory.id_of(
                            code="answer-always",
                            project_question_id=self.project_question_id,
                        ),
                        text="Always",
                        description=None,
                        selected=False,
                    ),
                    ProjectAnswerFactory.create_project_answer(
                        answer_id=ProjectAnswerFactory.id_of(
                            code="answer-never",
                            project_question_id=self.project_question_id,
                        ),
                        text="Never",
                        description=None,
                        selected=False,
                    ),
                }
            ),
            created_at=self.question_timestamp,
        )

    def test_select_answer(self):
        answer, _ = self.question.answers
        question: ProjectQuestion = self.question.select_answer(answer.id)
        expected_answers: FrozenSet[ProjectAnswer] = self.question.answers.difference(
            {answer}
        ).union({answer.select()})
        self.assertEqual(question.answers, expected_answers)

    def test_select_more_than_one_answer(self):
        answer1, answer2 = self.question.answers
        question: ProjectQuestion = self.question.select_answer(
            answer1.id
        ).select_answer(answer2.id)
        expected_answers: FrozenSet[ProjectAnswer] = self.question.answers.difference(
            {answer1, answer2}
        ).union({answer1.select(), answer2.select()})
        self.assertEqual(question.answers, expected_answers)

    def test_select_answer_twice(self):
        answer, _ = self.question.answers
        question: ProjectQuestion = self.question.select_answer(
            answer.id
        ).select_answer(answer.id)
        expected_answers: FrozenSet[ProjectAnswer] = self.question.answers.difference(
            {answer}
        ).union({answer.select()})
        self.assertEqual(question.answers, expected_answers)

    def test_select_wrong_answer(self):
        self.assertRaises(
            ValueError,
            lambda: self.question.select_answer(
                ProjectAnswerFactory.id_of(
                    code="wrong-answer-id", project_question_id=self.project_question_id
                )
            ),
        )

    def test_deselect_answer(self):
        answer, _ = self.question.answers
        expected_answers: FrozenSet[ProjectAnswer] = self.question.answers.difference(
            {answer}
        ).union({answer.deselect()})
        question: ProjectQuestion = self.question.select_answer(
            answer.id
        ).deselect_answer(answer.id)
        self.assertEqual(question.answers, expected_answers)

    def test_deselect_more_than_one_answer(self):
        answer1, answer2 = self.question.answers
        expected_answers: FrozenSet[ProjectAnswer] = self.question.answers.difference(
            {answer1, answer2}
        ).union({answer1.deselect(), answer2.deselect()})
        question: ProjectQuestion = (
            self.question.select_answer(answer1.id)
            .select_answer(answer2.id)
            .deselect_answer(answer1.id)
            .deselect_answer(answer2.id)
        )
        self.assertEqual(question.answers, expected_answers)

    def test_deselect_not_selected_answer(self):
        answer, _ = self.question.answers
        expected_answers: FrozenSet[ProjectAnswer] = self.question.answers
        question: ProjectQuestion = self.question.deselect_answer(answer.id)
        self.assertEqual(question.answers, expected_answers)


class TestBooleanProjectQuestion(unittest.TestCase):
    def setUp(self):
        self.project_id: EntityId = ProjectFactory.id_of(code="project_id")
        self.project_question_id: EntityId = ProjectQuestionFactory.id_of(
            code="boolean_question_id", project_id=self.project_id
        )
        self.project_question: ProjectQuestion = (
            ProjectQuestionFactory.create_project_boolean_question(
                self.project_question_id,
                "Do you practice TDD?",
            )
        )

    def test_boolean_answers(self):
        self.assertEqual(
            self.project_question.answers,
            frozenset(
                {
                    ProjectAnswerFactory.create_project_answer(
                        ProjectAnswerFactory.id_of(
                            code="true", project_question_id=self.project_question_id
                        ),
                        "Yes",
                    ),
                    ProjectAnswerFactory.create_project_answer(
                        ProjectAnswerFactory.id_of(
                            code="false", project_question_id=self.project_question_id
                        ),
                        "No",
                    ),
                }
            ),
        )
