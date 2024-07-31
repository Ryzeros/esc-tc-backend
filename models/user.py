from sqlalchemy import Column, String, Boolean, Integer, UniqueConstraint
from config.database import Base


class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True)
    password = Column(String)
    disabled = Column(Boolean, default=False)
    roles = Column(String)
    partner_code = Column(String)

    __table_args__ = (
        UniqueConstraint('email', name='uix_2'),
    )
