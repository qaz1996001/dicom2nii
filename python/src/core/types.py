"""
型別定義和型別別名
"""

from concurrent.futures import Executor
from pathlib import Path
from typing import Any, Optional, Protocol, Union

from pydicom import FileDataset

# 路徑型別
PathLike = Union[str, Path]

# 處理結果型別
ProcessingResult = dict[str, Any]

# 策略列表型別
StrategyList = list['ProcessingStrategy']

# 執行器型別
ExecutorType = Optional[Executor]


class ProcessingStrategy(Protocol):
    """處理策略協議"""

    def process(self, *args, **kwargs) -> Any:
        """處理方法"""
        ...


class Manager(Protocol):
    """管理器協議"""

    def run(self, executor: ExecutorType = None) -> None:
        """執行方法"""
        ...


class Converter(Protocol):
    """轉換器協議"""

    def convert(self, *args, **kwargs) -> Any:
        """轉換方法"""
        ...


# DICOM 相關型別
DicomDataset = FileDataset
DicomTag = tuple[int, int]

# 配置型別
ConfigDict = dict[str, Any]
