from sqlalchemy.orm import Session

from src.core.interfaces.unit_of_work import UnitOfWorkInterface


class SQLAlchemyUnitOfWork(UnitOfWorkInterface):
    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()