from sqlalchemy import Column, Integer, String
from app.utils.db import Base

class RelationshipType(Base):
    __tablename__ = "relationship_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # 예: MOTHER, FATHER
    display_name_ko = Column(String, nullable=False) # 예: 어머니, 아버지
