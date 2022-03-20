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
    def _is_monday() -> bool:
        return datetime.date.today().weekday() == 0

    @staticmethod
    def _is_tuesday() -> bool:
        return datetime.date.today().weekday() == 1

    @staticmethod
    def _is_wednesday() -> bool:
        return datetime.date.today().weekday() == 2

    @staticmethod
    def _is_thursday() -> bool:
        return datetime.date.today().weekday() == 3

    @staticmethod
    def _is_friday() -> bool:
        return datetime.date.today().weekday() == 4
