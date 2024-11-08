from typing import Optional

from domain.common.core import EntityId
from domain.project.core import ProjectAnswer


class ProjectAnswerFactory:

    @staticmethod
    def id_of(code: str, project_question_id: EntityId) -> EntityId:
        return EntityId(
            code=code,
            question_code=project_question_id.code,
            project_code=project_question_id.project_code,
        )

    @staticmethod
    def create_project_answer(
        answer_id: EntityId,
        text: str,
        description: Optional[str] = None,
        selected: bool = False,
    ) -> ProjectAnswer:
        return ProjectAnswer(
            id=answer_id,
            text=text,
            description=description,
            selected=selected,
        )
