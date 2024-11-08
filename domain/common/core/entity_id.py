import json

from pydantic import BaseModel, ConfigDict


class EntityId(BaseModel):
    model_config = ConfigDict(extra="allow")

    def __init__(self, **kwargs):
        if len(kwargs) == 0:
            raise ValueError("EntityId must have at least one attribute")
        for k, v in kwargs.items():
            try:
                hash(v)
            except TypeError:
                raise ValueError(
                    f"EntityId attributes must be hashable, got {k}={v}, whose value is not hashable"
                )
        super().__init__(**kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k}={v}' for k, v in self.model_extra.items()])})"

    def __hash__(self):
        return hash(tuple(self.model_extra.items()))

    def model_dump_json(self, **kwargs) -> str:
        return json.dumps(self.model_extra)

    @property
    def keys(self):
        return self.model_extra.keys()

    @property
    def values(self):
        return self.model_extra.values()
