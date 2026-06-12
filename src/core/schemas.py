from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_orm(cls, obj, **kwargs):
        return cls.model_validate(obj, **kwargs)

    def to_dict(self, *args, **kwargs) -> dict[str, Any]:
        return self.model_dump(*args, **kwargs)
