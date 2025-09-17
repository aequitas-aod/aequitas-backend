import json

import yaml

from domain.common.core import EntityId
from domain.graph.core import GraphQuestion
from domain.project.core import ProjectQuestion
from presentation.presentation import deserialize, serialize
from test.integration.project import ProjectRelatedTestCase
from test.resources import example_question_graph


class TestQuestionnairesAPI(ProjectRelatedTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project_name: str = "Project name"
        cls.project_id: EntityId = cls._create_project(cls.project_name)
        questions_yaml: str = example_question_graph()
        cls.app.post("/questions/load", content_type="text/yaml", data=questions_yaml)
        cls.questions: list[GraphQuestion] = [
            deserialize(q, GraphQuestion) for q in yaml.safe_load(questions_yaml)
        ]

    def tearDown(self):
        self._reset_questionnaire()

    def _reset_questionnaire(self):
        self.app.delete(f"/projects/{self.project_id.code}/questionnaire")

    def _compare_graph_and_project_questions(
        self, q1: ProjectQuestion, q2: GraphQuestion
    ):
        self.assertEqual(q1.id.code, q2.id.code)
        self.assertEqual(self.project_id.code, q1.id.project_code)
        self.assertEqual(q1.text, q2.text)
        self.assertEqual(q1.type, q2.type)
        self.assertEqual(
            frozenset([a.text for a in q1.answers]),
            frozenset([a.text for a in q2.answers]),
        )

    def _get_nth_question(self, project_code: str, index: int) -> ProjectQuestion:
        response = self.app.get(f"/projects/{project_code}/questionnaire/{index}")
        self.assertEqual(response.status_code, 200)
        return deserialize(json.loads(response.data), ProjectQuestion)

    def _select_answer_to_nth_question(
        self, project_code: str, index: int, project_answer_id: EntityId
    ):
        serialized_answer_id = serialize(project_answer_id)
        response = self.app.put(
            f"/projects/{project_code}/questionnaire/{index}",
            json={"answer_ids": [serialized_answer_id]},
        )
        self.assertEqual(response.status_code, 200)

    def _get_question_from_questionnaire_and_graph(
        self, index: int
    ) -> (ProjectQuestion, GraphQuestion):
        project_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, index
        )
        response = self.app.get(f"questions/{self.questions[index - 1].id.code}")
        related_question: GraphQuestion = deserialize(
            json.loads(response.data), GraphQuestion
        )
        return project_question, related_question

    def test_get_first_question(self):
        first_question, related_question = (
            self._get_question_from_questionnaire_and_graph(1)
        )
        self._compare_graph_and_project_questions(first_question, related_question)

    def test_select_answer_to_first_question(self):
        first_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 1
        )
        answer = sorted(first_question.answers, key=lambda a: a.id.code)[0]
        expected_question: ProjectQuestion = first_question.select_answer(answer.id)
        self._select_answer_to_nth_question(self.project_id.code, 1, answer.id)
        selected_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 1
        )
        self.assertEqual(set(selected_question.answers), set(expected_question.answers))
        new_question, related_question = (
            self._get_question_from_questionnaire_and_graph(2)
        )
        self._compare_graph_and_project_questions(new_question, related_question)

    def test_get_not_already_existing_nth_question(self):
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/4")
        self.assertEqual(response.status_code, 404)
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire/5")
        self.assertEqual(response.status_code, 404)

    def test_select_wrong_answer(self):
        response = self.app.put(
            f"/projects/{self.project_id.code}/questionnaire/1",
            json={"answer_ids": ["not-existing"]},
        )
        self.assertEqual(response.status_code, 400)

    def test_select_answers_until_third_question(self):
        first_question, related_question = (
            self._get_question_from_questionnaire_and_graph(1)
        )
        self._compare_graph_and_project_questions(first_question, related_question)
        answer = sorted(first_question.answers, key=lambda a: a.id.code)[0]
        self._select_answer_to_nth_question(self.project_id.code, 1, answer.id)
        second_question, related_question = (
            self._get_question_from_questionnaire_and_graph(2)
        )
        self._compare_graph_and_project_questions(second_question, related_question)
        answer = sorted(second_question.answers, key=lambda a: a.id.code)[0]
        self._select_answer_to_nth_question(self.project_id.code, 2, answer.id)
        third_question, related_question = (
            self._get_question_from_questionnaire_and_graph(3)
        )
        self._compare_graph_and_project_questions(third_question, related_question)
        answer = sorted(third_question.answers, key=lambda a: a.id.code)[0]
        self._select_answer_to_nth_question(self.project_id.code, 3, answer.id)
        expected_question: ProjectQuestion = third_question.select_answer(answer.id)
        selected_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 3
        )
        self.assertEqual(set(selected_question.answers), set(expected_question.answers))

    def test_change_selected_answers(self):
        first_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 1
        )
        answers_iter = iter(first_question.answers)
        answer = next(answers_iter)
        self._select_answer_to_nth_question(self.project_id.code, 1, answer.id)
        new_answer = next(answers_iter)
        expected_selected_answers = first_question.select_answer(new_answer.id).answers
        self._select_answer_to_nth_question(self.project_id.code, 1, new_answer.id)
        selected_answers = self._get_nth_question(self.project_id.code, 1).answers
        self.assertEqual(selected_answers, expected_selected_answers)

    def test_remove_question(self):
        response = self.app.delete(f"/projects/{self.project_id.code}/questionnaire/3")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'"No questions exist in the questionnaire"\n')
        first_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 1
        )
        answer = next(iter(first_question.answers))
        self._select_answer_to_nth_question(self.project_id.code, 1, answer.id)
        response = self.app.delete(f"/projects/{self.project_id.code}/questionnaire/1")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data, b'"Question was not the last in the questionnaire"\n'
        )
        response = self.app.delete(f"/projects/{self.project_id.code}/questionnaire/2")
        self.assertEqual(response.status_code, 200)

    def test_reset_questionnaire(self):
        first_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 1
        )
        answer = next(iter(first_question.answers))
        self._select_answer_to_nth_question(self.project_id.code, 1, answer.id)
        second_question: ProjectQuestion = self._get_nth_question(
            self.project_id.code, 2
        )
        answer = next(iter(second_question.answers))
        self._select_answer_to_nth_question(self.project_id.code, 2, answer.id)
        response = self.app.delete(f"/projects/{self.project_id.code}/questionnaire")
        self.assertEqual(response.status_code, 200)
        response = self.app.get(f"/projects/{self.project_id.code}/questionnaire")
        self.assertEqual(response.data, b"[]\n")

    def test_get_final_question(self):
        for i in range(1, len(self.questions) + 1):
            question = self._get_nth_question(self.project_id.code, i)
            answer = next(iter(question.answers))
            self._select_answer_to_nth_question(self.project_id.code, i, answer.id)

        response = self.app.get(
            f"/projects/{self.project_id.code}/questionnaire/{len(self.questions) + 1}"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'"Questionnaire is finished"\n')
        response = self.app.get(
            f"/projects/{self.project_id.code}/questionnaire/{len(self.questions) + 5}"
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, b'"Question not found"\n')

    def test_multiple_questionnaires(self):
        project_name_2: str = "Project name 2"
        project_id_2: EntityId = self._create_project(project_name_2)

        for i in range(1, len(self.questions) + 1):
            question_1 = self._get_nth_question(self.project_id.code, i)
            question_2 = self._get_nth_question(project_id_2.code, i)
            answer_1 = next(iter(question_1.answers))
            answer_2 = next(iter(question_2.answers))
            self._select_answer_to_nth_question(self.project_id.code, i, answer_1.id)
            self._select_answer_to_nth_question(project_id_2.code, i, answer_2.id)

        response = self.app.get(
            f"/projects/{self.project_id.code}/questionnaire/{len(self.questions) + 1}"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'"Questionnaire is finished"\n')

        response = self.app.get(
            f"/projects/{project_id_2.code}/questionnaire/{len(self.questions) + 1}"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, b'"Questionnaire is finished"\n')
