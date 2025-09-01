"""
管理器基礎類別 - 遵循錯誤處理規則
"""

from abc import ABCMeta, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from ..core.config import Config
from ..core.exceptions import (
    ProcessingError,
    validate_required_params,
)
from ..core.logging import StructuredLogger, get_logger
from ..core.types import ExecutorType, PathLike


class BaseManager(metaclass=ABCMeta):
    """管理器基礎類別 - 實施 Guard Clauses 和結構化日誌"""

    def __init__(self, input_path: PathLike, **kwargs):
        """初始化管理器 - 實施 Early Return 驗證模式

        Args:
            input_path: 輸入路徑
            **kwargs: 其他參數
        """
        # Guard Clauses - Early Return 模式
        validate_required_params(input_path=input_path)

        self._input_path = Path(input_path)

        # 驗證路徑存在性
        if not self._input_path.exists():
            raise ProcessingError(
                f"輸入路徑不存在: {input_path}",
                processing_stage="initialization",
                details={"input_path": str(input_path)}
            )

        # 初始化結構化日誌記錄器
        self._logger: StructuredLogger = get_logger(f"manager.{self.__class__.__name__.lower()}")

    @property
    def input_path(self) -> Path:
        """獲取輸入路徑"""
        return self._input_path

    @input_path.setter
    def input_path(self, value: PathLike) -> None:
        """設定輸入路徑"""
        self._input_path = Path(value)

    @abstractmethod
    def run(self, executor: ExecutorType = None) -> None:
        """抽象執行方法

        Args:
            executor: 執行器，用於並行處理
        """
        pass

    def _is_directory_structure(self) -> bool:
        """檢查輸入路徑是否為目錄結構"""
        try:
            items = list(self.input_path.iterdir())
            return all(item.is_dir() for item in items)
        except Exception:
            return False

    def _get_study_paths(self) -> list[Path]:
        """獲取檢查路徑列表"""
        if self._is_directory_structure():
            return list(self.input_path.iterdir())
        else:
            return [self.input_path]

    def _validate_worker_count(self, worker_count: int) -> int:
        """驗證並調整工作執行緒數量"""
        return Config.get_worker_count(worker_count)

    def _create_executor(self, worker_count: int) -> ThreadPoolExecutor:
        """建立執行器"""
        validated_count = self._validate_worker_count(worker_count)
        return ThreadPoolExecutor(max_workers=validated_count)

    def _log_progress(self, message: str, study_name: str = None) -> None:
        """記錄進度"""
        if study_name:
            print(f"[{study_name}] {message}")
        else:
            print(message)

    def _handle_processing_error(self, error: Exception, context: str) -> None:
        """處理錯誤 - 遵循結構化日誌記錄規則"""
        # 轉換為專案例外 (如果不是的話)
        if not isinstance(error, ProcessingError):
            processing_error = ProcessingError(
                f"{context}: {str(error)}",
                processing_stage=context,
                cause=error
            )
        else:
            processing_error = error

        # 結構化日誌記錄
        self._logger.log_error(processing_error, context={"manager": self.__class__.__name__})

        # 不重新拋出，讓呼叫者決定如何處理
