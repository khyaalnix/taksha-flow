from pydantic import BaseModel, Field, field_validator, PrivateAttr, model_validator
from uuid import UUID
from typing import Optional, Dict, Any, Generic, TypeVar, List, Union
from datetime import datetime, timezone

T = TypeVar('T')

class MetaData(BaseModel):
    createdAt: str = Field(default_factory=lambda: str(datetime.now(timezone.utc)))
    updatedAt: Optional[str] = Field(default_factory=lambda: str(datetime.now(timezone.utc)))
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    version: int = Field(default=1)
    isActive: bool = Field(default=True)

    @field_validator("updatedAt", mode='before')
    @classmethod
    def set_updated_at_on_validate(cls, v: Optional[str]) -> str:
        """Ensures updatedAt is always set."""
        return v or str(datetime.now(timezone.utc))

    class Config:
        populate_by_name = True # Corrected from 'population_name'
        json_encoders = {
            UUID: str,
            datetime: lambda v: str(v.isoformat()) # Using ISO format is standard
        }

class Entity(MetaData):
    """
    Base entity model that provides common fields and functionality for all models.
    Includes identifier and metadata tracking.
    """
    id: Optional[str] = None

    def update(self, data: MetaData, updated_by_user: str):
        if self.version > data.version:
            raise ValueError(
                f"Cannot update with older version. Current version: {self.metadata.version}, Provided: {data.version}")

        # Update fields from the incoming data object
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        # Increment version and set update info
        self.version += 1
        self.updatedAt = str(datetime.now(timezone.utc))
        self.updatedBy = updated_by_user

    @property
    def metadata(self) -> MetaData:
        """
        This is done to avoid large code refactors using the getter property
        hence, campaign.metadata can be used just like before
        """
        metadata_dict = self.model_dump(include=MetaData.model_fields.keys())
        return MetaData.model_validate(metadata_dict)

    @metadata.setter
    def metadata(self,new_metadata: MetaData):
        """
        SETTER: Unpacks a MetaData object and applies its values to the entity.
        This allows you to set `campaign.metadata = ...` just like before.
        """
        for field_name in MetaData.model_fields.keys():
            new_value = getattr(new_metadata, field_name)
            setattr(self, field_name, new_value)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id if isinstance(other, Entity) else False

    class Config:
        populate_by_name = True

class NamedEntity(Entity):
    name: str


class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    pages: int

class Response(BaseModel, Generic[T]):
    message: str
    pagination: PaginationInfo

class ListResponse(Response[T]):
    data: List[T]

class GenericResponse(Response[Dict[str, Any]]):
    data: Dict[str, Any]