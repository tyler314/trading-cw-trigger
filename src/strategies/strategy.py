from abc import ABC, abstractmethod
from utils.common_utils import AssetType
import datetime


class Strategy(ABC):
    @abstractmethod
    def execute(self) -> dict:
        pass

    @abstractmethod
    def asset_type(self) -> AssetType:
        pass

    @staticmethod
    def _is_monday():
        return datetime.date.today().weekday() == 0

    @staticmethod
    def _is_tuesday():
        return datetime.date.today().weekday() == 1

    @staticmethod
    def _is_wednesday():
        return datetime.date.today().weekday() == 2

    @staticmethod
    def _is_thursday():
        return datetime.date.today().weekday() == 3

    @staticmethod
    def _is_friday():
        return datetime.date.today().weekday() == 4
