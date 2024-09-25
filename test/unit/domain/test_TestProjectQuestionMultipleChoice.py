import unittest
from datetime import datetime
from typing import FrozenSet

from domain.common.core import AnswerId, QuestionId
from domain.common.core.enum import QuestionType
from domain.project.core import ProjectQuestion, ProjectAnswer, ProjectId
from domain.project.factories import ProjectQuestionFactory, ProjectAnswerFactory


class TestProjectQuestionSingleChoice(unittest.TestCase):

    def setUp(self):
        self.question_timestamp = datetime.now()
        self.question: ProjectQuestion = ProjectQuestionFactory.create_project_question(
            QuestionId(code="question_id"),
            "Do you practice TDD?",
            QuestionType.MULTIPLE_CHOICE,
            frozenset(
                {
                    ProjectAnswer(
                        id=AnswerId(code="answer-always"),
                        text="Always",
                        selected=False,
                    ),
                    ProjectAnswer(
                        id=AnswerId(code="answer-never"),
                        text="Never",
                        selected=False,
                    ),
                }
            ),
            ProjectId(code="project_id"),
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
            lambda: self.question.select_answer(AnswerId(code="wrong-answer-id")),
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
        self.project_question: ProjectQuestion = (
            ProjectQuestionFactory.create_project_boolean_question(
                QuestionId(code="boolean_question_id"),
                "Do you practice TDD?",
                ProjectId(code="project_id"),
            )
        )

    def test_boolean_answers(self):
        self.assertEqual(
            self.project_question.answers,
            frozenset(
                {
                    ProjectAnswerFactory.create_project_answer(
                        AnswerId(code="boolean_question_id-true"), "Yes"
                    ),
                    ProjectAnswerFactory.create_project_answer(
                        AnswerId(code="boolean_question_id-false"), "No"
                    ),
                }
            ),
        )
