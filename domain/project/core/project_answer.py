from typing_extensions import Self

from domain.common.core import Answer


class ProjectAnswer(Answer):
    selected: bool

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def select(self) -> Self:
        """
        Selects the answer
        :return: ProjectAnswer a new instance of ProjectAnswer with selected=True
        """
        return ProjectAnswer(id=self.id, text=self.text, selected=True)

    def deselect(self) -> Self:
        """
        Deselects the answer
        :return: ProjectAnswer a new instance of ProjectAnswer with selected=False
        """
        return ProjectAnswer(id=self.id, text=self.text, selected=False)

    def __str__(self):
        return (
            f"Answer(\n id={self.id},\n text={self.text},\n selected={self.selected}\n)"
        )

    def __hash__(self):
        return hash((self.id.code, self.text, self.selected))
