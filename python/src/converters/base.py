"""
轉換器基礎類別
"""

from abc import ABCMeta, abstractmethod
from pathlib import Path

from ..core.exceptions import ConversionError
from ..core.types import ExecutorType, PathLike


class BaseConverter(metaclass=ABCMeta):
    """轉換器基礎類別"""

    def __init__(self, input_path: PathLike, output_path: PathLike):
        """初始化轉換器

        Args:
            input_path: 輸入路徑
            output_path: 輸出路徑
        """
        self._input_path = Path(input_path)
        self._output_path = Path(output_path)
        self._exclude_set: set[str] = set()

        # 驗證路徑
        if not self._input_path.exists():
            raise ConversionError(f"輸入路徑不存在: {input_path}")

    @property
    def input_path(self) -> Path:
        """獲取輸入路徑"""
        return self._input_path

    @property
    def output_path(self) -> Path:
        """獲取輸出路徑"""
        return self._output_path

    @property
    def exclude_set(self) -> set[str]:
        """獲取排除集合"""
        return self._exclude_set

    @exclude_set.setter
    def exclude_set(self, value: set[str]) -> None:
        """設定排除集合"""
        self._exclude_set = value

    @abstractmethod
    def convert(self, executor: ExecutorType = None) -> None:
        """抽象轉換方法

        Args:
            executor: 執行器，用於並行處理
        """
        pass

    def _ensure_output_directory(self, path: Path) -> None:
        """確保輸出目錄存在"""
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConversionError(f"無法建立輸出目錄 {path.parent}: {str(e)}") from e

    def _is_excluded(self, name: str) -> bool:
        """檢查是否應該排除"""
        return name in self._exclude_set

    def _copy_metadata(self, source_study_path: Path) -> None:
        """複製元資料目錄"""
        try:
            meta_path = source_study_path / ".meta"
            if meta_path.exists():
                from ..utils.file_operations import copy_directory_tree

                output_study_path = self._get_output_study_path(source_study_path)
                output_meta_path = output_study_path / ".meta"
                copy_directory_tree(meta_path, output_meta_path, dirs_exist_ok=True)
        except Exception as e:
            raise ConversionError(f"複製元資料失敗: {str(e)}") from e

    def _get_output_study_path(self, input_study_path: Path) -> Path:
        """獲取輸出檢查路徑"""
        relative_path = input_study_path.relative_to(self._input_path.parent)
        return self._output_path / relative_path.parts[-1]  # 只取最後一部分

    def _validate_conversion_result(self, input_file: Path, output_file: Path) -> bool:
        """驗證轉換結果"""
        try:
            return output_file.exists() and output_file.stat().st_size > 0
        except Exception:
            return False
