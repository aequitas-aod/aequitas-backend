from typing_extensions import Self

from domain.common.core import Answer, EntityId


class ProjectAnswer(Answer):
    id: EntityId
    selected: bool

    def select(self) -> Self:
        """
        Selects the answer
        :return: ProjectAnswer a new instance of ProjectAnswer with selected=True
        """
        return ProjectAnswer(
            id=self.id, text=self.text, description=self.description, selected=True
        )

    def deselect(self) -> Self:
        """
        Deselects the answer
        :return: ProjectAnswer a new instance of ProjectAnswer with selected=False
        """
        return ProjectAnswer(
            id=self.id, text=self.text, description=self.description, selected=False
        )

    def __str__(self):
        return f"Answer(\n id={self.id},\n text={self.text},\n description={self.description},\n selected={self.selected}\n)"

    def __hash__(self):
        return hash((self.id, self.text, self.selected))
