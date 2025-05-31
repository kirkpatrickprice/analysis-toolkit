from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class KPATBaseModel(BaseModel):
    """Base model class for all models in the KP Analysis Toolkit."""

    # Enable arbitrary types to handle Path objects and callables
    class Config:
        arbitrary_types_allowed = True
