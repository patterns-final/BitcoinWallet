from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    api_key = Column(String, nullable=False, unique=True, index=True)

    wallets = relationship("WalletModel", back_populates="user", lazy="joined")


class WalletModel(Base):
    __tablename__ = "wallets"

    id = Column(String, primary_key=True)
    address = Column(String, nullable=False, unique=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    balance_satoshi = Column(Integer, nullable=False)

    user = relationship("UserModel", back_populates="wallets")


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    from_wallet_address = Column(String, ForeignKey("wallets.address"), nullable=False, index=True)
    to_wallet_address = Column(String, ForeignKey("wallets.address"), nullable=False, index=True)
    amount_satoshis = Column(Integer, nullable=False)
    fee_satoshis = Column(Integer, nullable=False)
    is_internal_transfer = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)