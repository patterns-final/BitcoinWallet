from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True, nullable=False)

    wallets = relationship("WalletModel", back_populates="user", cascade="all, delete-orphan")
