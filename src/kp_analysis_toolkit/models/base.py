from typing import TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class KPATBaseModel(BaseModel):
    """Base model class for all models in the KP Analysis Toolkit."""

    # Enable arbitrary types to handle Path objects and callables
    model_config = ConfigDict(arbitrary_types_allowed=True)
