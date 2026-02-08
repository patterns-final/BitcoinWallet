from abc import ABC, abstractmethod


class UnitOfWorkInterface(ABC):
    @abstractmethod
    def commit(selfs):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError