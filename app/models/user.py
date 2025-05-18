from sqlalchemy import Column, Integer, String
from app.db.database import Base
from pydantic import BaseModel

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    requests_left = Column(Integer, default=20)

class UserOut(BaseModel):
    id: int
    username: str

    model_config = {
        "from_attributes": True
    }