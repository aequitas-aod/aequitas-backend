from domain.common.core import AnswerId
from domain.project.core import ProjectAnswer


class ProjectAnswerFactory:

    @staticmethod
    def create_project_answer(
        project_answer_id: AnswerId, text: str, selected: bool = False
    ) -> ProjectAnswer:
        return ProjectAnswer(id=project_answer_id, text=text, selected=selected)
