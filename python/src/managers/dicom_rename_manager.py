"""
DICOM 重新命名管理器 - 基於原始邏輯重構
"""

import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Union

from tqdm import tqdm

try:
    import pydicom.errors
    from pydicom import FileDataset, dcmread
except ImportError:

    class FileDataset:
        pass


from ..core.config import Config
from ..core.enums import NullEnum
from ..core.exceptions import DicomParsingError, ProcessingError
from ..core.logging import get_logger
from ..core.types import DicomDataset, ExecutorType
from ..processing.base import (
    ModalityProcessingStrategy,
    MRAcquisitionTypeProcessingStrategy,
)
from ..processing.factory import ProcessingStrategyFactory
from .base import BaseManager


class DicomRenameManager(BaseManager):
    """DICOM 重新命名管理器 - 實作正確的重新命名邏輯"""

    def __init__(self, input_path: Union[str, Path], output_path: Union[str, Path]):
        """初始化 DICOM 重新命名管理器

        Args:
            input_path: 輸入 DICOM 路徑
            output_path: 輸出重新命名 DICOM 路徑
        """
        super().__init__(input_path)
        self.output_path = Path(output_path)

        # 初始化處理策略
        self.modality_processing_strategy = ModalityProcessingStrategy()
        self.mr_acquisition_type_processing_strategy = (
            MRAcquisitionTypeProcessingStrategy()
        )
        self.processing_strategy_list = (
            ProcessingStrategyFactory.create_all_mr_strategies()
        )

        # 初始化日誌記錄器
        self._logger = get_logger("dicom_rename_manager")

    def get_study_folder_name(self, dicom_ds: DicomDataset) -> Optional[str]:
        """根據 DICOM 資料集生成檢查資料夾名稱 - 純函數"""
        try:
            modality = dicom_ds[0x08, 0x60].value
            patient_id = dicom_ds[0x10, 0x20].value
            accession_number = dicom_ds[0x08, 0x50].value
            series_date = dicom_ds.get((0x08, 0x21), None)

            if series_date is None:
                return None

            series_date_value = series_date.value
            return f"{patient_id}_{series_date_value}_{modality}_{accession_number}"

        except Exception as e:
            self._logger.log_error(e, context={"operation": "get_study_folder_name"})
            return None

    def get_output_study_path(self, dicom_ds: DicomDataset) -> Optional[Path]:
        """獲取輸出檢查路徑"""
        study_folder_name = self.get_study_folder_name(dicom_ds)

        if not study_folder_name:
            return None

        # 如果輸出路徑已經是檢查資料夾，直接返回
        if self.output_path.name == study_folder_name:
            return self.output_path

        # 否則在輸出路徑下建立檢查資料夾
        return self.output_path / study_folder_name

    def determine_series_name(self, dicom_ds: DicomDataset) -> str:
        """決定序列重新命名 - 使用策略模式"""
        try:
            # 獲取模態
            modality_enum = self.modality_processing_strategy.process(dicom_ds)
            mr_acquisition_type_enum = (
                self.mr_acquisition_type_processing_strategy.process(dicom_ds)
            )

            # 遍歷所有處理策略
            for processing_strategy in self.processing_strategy_list:
                if modality_enum == processing_strategy.modality:
                    for mr_acquisition_type in processing_strategy.mr_acquisition_type:
                        if mr_acquisition_type_enum == mr_acquisition_type:
                            series_enum = processing_strategy.process(dicom_ds)
                            if series_enum is not NullEnum.NULL:
                                return series_enum.value

            return ""

        except Exception as e:
            self._logger.log_error(e, context={"operation": "determine_series_name"})
            return ""

    def process_single_dicom_file(self, dicom_file_path: Path) -> bool:
        """處理單一 DICOM 檔案 - 遵循 .cursor 規則的函數式實作"""
        try:
            # Early Return - 檢查檔案是否為 DICOM
            if not dicom_file_path.name.endswith(".dcm"):
                return False

            # 讀取 DICOM 檔案
            dicom_ds = dcmread(str(dicom_file_path), stop_before_pixels=True)

            # 獲取輸出檢查路徑
            output_study_path = self.get_output_study_path(dicom_ds)
            if not output_study_path:
                return False

            # 決定序列名稱
            series_name = self.determine_series_name(dicom_ds)
            if not series_name:
                return False

            # 建立輸出目錄結構
            output_study_path.mkdir(parents=True, exist_ok=True)
            output_series_path = output_study_path / series_name
            output_series_path.mkdir(exist_ok=True)

            # 複製檔案到新位置
            output_file_path = output_series_path / dicom_file_path.name
            if not output_file_path.exists():
                shutil.copyfile(dicom_file_path, output_file_path)

            return True

        except (
            pydicom.errors.InvalidDicomError,
            pydicom.errors.BytesLengthException,
        ) as e:
            self._logger.log_error(
                DicomParsingError(
                    f"DICOM 檔案解析失敗: {str(e)}", dicom_file=str(dicom_file_path)
                ),
                context={"file": str(dicom_file_path)},
            )
            return False
        except Exception as e:
            self._logger.log_error(
                e,
                context={
                    "file": str(dicom_file_path),
                    "operation": "process_single_dicom_file",
                },
            )
            return False

    def run(self, executor: ExecutorType = None) -> None:
        """執行 DICOM 重新命名"""
        try:
            self._log_progress("開始 DICOM 重新命名處理")

            # 尋找所有 DICOM 檔案
            dicom_files = list(self.input_path.rglob("*.dcm"))

            if not dicom_files:
                raise ProcessingError("在輸入路徑中找不到 DICOM 檔案")

            self._log_progress(f"找到 {len(dicom_files)} 個 DICOM 檔案")

            # 處理檔案
            if executor:
                self._process_with_executor(dicom_files, executor)
            else:
                with self._create_executor(
                    Config.DEFAULT_WORKER_COUNT
                ) as rename_executor:
                    self._process_with_executor(dicom_files, rename_executor)

            self._log_progress("DICOM 重新命名完成")

        except Exception as e:
            raise ProcessingError(f"DICOM 重新命名執行失敗: {str(e)}")

    def _process_with_executor(
        self, dicom_files: List[Path], executor: ThreadPoolExecutor
    ) -> None:
        """使用執行器處理 DICOM 檔案"""
        futures = []

        # 提交所有處理任務
        for dicom_file in tqdm(dicom_files, desc="提交 DICOM 處理任務"):
            future = executor.submit(self.process_single_dicom_file, dicom_file)
            futures.append(future)

        # 等待所有任務完成並收集結果
        successful_count = 0
        failed_count = 0

        for future in tqdm(futures, desc="等待處理完成"):
            try:
                result = future.result()
                if result:
                    successful_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
                self._handle_processing_error(e, "DICOM 檔案處理")

        self._log_progress(f"處理完成: 成功 {successful_count}, 失敗 {failed_count}")

    def get_processing_statistics(self) -> dict:
        """獲取處理統計資訊"""
        try:
            input_dicom_count = len(list(self.input_path.rglob("*.dcm")))
            output_dicom_count = (
                len(list(self.output_path.rglob("*.dcm")))
                if self.output_path.exists()
                else 0
            )

            return {
                "input_dicom_files": input_dicom_count,
                "output_dicom_files": output_dicom_count,
                "processing_rate": output_dicom_count / input_dicom_count
                if input_dicom_count > 0
                else 0,
                "available_strategies": len(self.processing_strategy_list),
            }
        except Exception as e:
            self._handle_processing_error(e, "獲取處理統計")
            return {}
