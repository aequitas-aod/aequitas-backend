from typing import Optional

from domain.common.core import Answer, EntityId


class AnswerFactory:

    @staticmethod
    def id_of(code: str, question_id: EntityId) -> EntityId:
        return EntityId(code=code, question_code=question_id.code)

    @staticmethod
    def create_answer(
        answer_id: EntityId, text: str, description: Optional[str] = None
    ) -> Answer:
        return Answer(id=answer_id, text=text, description=description)

    @staticmethod
    def create_boolean_answer(
        answer_id: EntityId, value: bool, description: Optional[str] = None
    ) -> Answer:
        return Answer(
            id=answer_id, text="Yes" if value else "No", description=description
        )
