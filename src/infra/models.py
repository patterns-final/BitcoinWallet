from sqlalchemy import Column, String
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    api_key = Column(String, unique=True, index=True, nullable=False)

    wallets = relationship("WalletModel", back_populates="user", cascade="all, delete-orphan")

class WalletModel(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True, index=True)
    address = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    balance_satoshis = Column(Integer, nullable=False, default=0)

    user = relationship("UserModel", back_populates="wallets")
