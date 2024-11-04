from typing import Optional

from domain.common.core.answer import Answer, AnswerId


class AnswerFactory:

    @staticmethod
    def create_answer(
        answer_id: AnswerId, text: str, description: Optional[str] = None
    ):
        return Answer(id=answer_id, text=text, description=description)

    @staticmethod
    def create_boolean_answer(
        answer_id: AnswerId, value: bool, description: Optional[str] = None
    ):
        return Answer(
            id=answer_id, text="Yes" if value else "No", description=description
        )
