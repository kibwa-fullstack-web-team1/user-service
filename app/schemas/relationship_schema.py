from pydantic import BaseModel, ConfigDict

class RelationshipTypeBase(BaseModel):
    name: str
    display_name_ko: str

class RelationshipTypeCreate(RelationshipTypeBase):
    pass

class RelationshipType(RelationshipTypeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
