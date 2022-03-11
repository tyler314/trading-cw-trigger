from abc import ABC, abstractmethod
from utils.common_utils import AssetType


class Strategy(ABC):
    @abstractmethod
    def execute(self) -> dict:
        pass

    @abstractmethod
    def asset_type(self) -> AssetType:
        pass
