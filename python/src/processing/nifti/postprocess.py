"""
NIfTI 後處理管理
"""

from pathlib import Path
from typing import Union

from ...core.exceptions import ProcessingError
from ...core.types import ExecutorType
from ..base import NiftiProcessingStrategy
from .strategies import (
    ADCNiftiProcessingStrategy,
    DwiNiftiProcessingStrategy,
    SWANNiftiProcessingStrategy,
    T1NiftiProcessingStrategy,
    T2NiftiProcessingStrategy,
)


class NiftiPostProcessManager:
    """NIfTI 後處理管理器"""

    def __init__(self, input_path: Union[str, Path]):
        """初始化後處理管理器

        Args:
            input_path: 輸入路徑
        """
        self._input_path = Path(input_path)
        self._processing_strategies: list[NiftiProcessingStrategy] = [
            DwiNiftiProcessingStrategy(),
            ADCNiftiProcessingStrategy(),
            SWANNiftiProcessingStrategy(),
            T1NiftiProcessingStrategy(),
            T2NiftiProcessingStrategy()
        ]

    @property
    def input_path(self) -> Path:
        """獲取輸入路徑"""
        return self._input_path

    @input_path.setter
    def input_path(self, value: Union[str, Path]) -> None:
        """設定輸入路徑"""
        self._input_path = Path(value)

    def post_process_study(self, study_path: Path) -> None:
        """後處理單一檢查"""
        try:
            # 先刪除 JSON 檔案
            self._delete_json_files(study_path)

            # 執行各種處理策略
            for strategy in self._processing_strategies:
                strategy.process(study_path)

        except Exception as e:
            raise ProcessingError(f"後處理檢查失敗 {study_path}: {str(e)}")

    def _delete_json_files(self, study_path: Path) -> None:
        """刪除 JSON 檔案"""
        json_files = [f for f in study_path.iterdir() if f.name.endswith('.json')]
        for json_file in json_files:
            json_file.unlink()

    def run(self, executor: ExecutorType = None) -> None:
        """執行後處理

        Args:
            executor: 執行器，用於並行處理
        """
        try:
            # 檢查是否所有項目都是目錄
            items = list(self.input_path.iterdir())
            is_all_directories = all(item.is_dir() for item in items)

            if is_all_directories:
                # 處理多個檢查
                study_paths = items
                for study_path in study_paths:
                    self.post_process_study(study_path)
            else:
                # 處理單一檢查
                self.post_process_study(self.input_path)

        except Exception as e:
            raise ProcessingError(f"NIfTI 後處理執行失敗: {str(e)}")

    def add_processing_strategy(self, strategy: NiftiProcessingStrategy) -> None:
        """添加新的處理策略"""
        self._processing_strategies.append(strategy)

    def remove_processing_strategy(self, strategy_type: type) -> None:
        """移除指定類型的處理策略"""
        self._processing_strategies = [
            s for s in self._processing_strategies
            if not isinstance(s, strategy_type)
        ]
