from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TransactionModel(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    from_wallet_address = Column(String, nullable=False, index=True)
    to_wallet_address = Column(String, nullable=False, index=True)
    amount_satoshis = Column(Integer, nullable=False)
    fee_satoshis = Column(Integer, nullable=False)
    is_internal_transfer = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)