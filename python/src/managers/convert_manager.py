"""
轉換管理器
"""

import time
from pathlib import Path
from typing import Optional, Union

from ..converters import DicomToNiftiConverter, NiftiToDicomConverter
from ..core.config import Config
from ..core.exceptions import ProcessingError
from ..core.types import ExecutorType
from ..processing.nifti.postprocess import NiftiPostProcessManager
from ..utils.reporting import generate_nifti_report, generate_study_report
from .base import BaseManager


class ConvertManager(BaseManager):
    """轉換管理器 - 統一管理所有轉換流程"""

    def __init__(
        self,
        input_path: Union[str, Path],
        output_dicom_path: Optional[Union[str, Path]] = None,
        output_nifti_path: Optional[Union[str, Path]] = None,
        worker_count: int = Config.DEFAULT_WORKER_COUNT,
    ):
        """初始化轉換管理器

        Args:
            input_path: 輸入路徑
            output_dicom_path: 輸出 DICOM 路徑
            output_nifti_path: 輸出 NIfTI 路徑
            worker_count: 工作執行緒數量
        """
        super().__init__(input_path)

        self.output_dicom_path = Path(output_dicom_path) if output_dicom_path else None
        self.output_nifti_path = Path(output_nifti_path) if output_nifti_path else None
        self.worker_count = self._validate_worker_count(worker_count)

        # 初始化轉換器
        self._dicom_to_nifti_converter: Optional[DicomToNiftiConverter] = None
        self._nifti_to_dicom_converter: Optional[NiftiToDicomConverter] = None
        self._nifti_postprocessor: Optional[NiftiPostProcessManager] = None

    def run(self, executor: ExecutorType = None) -> None:
        """執行完整的轉換流程

        Args:
            executor: 執行器，用於並行處理
        """
        try:
            start_time = time.time()

            # 判斷轉換類型並執行相應流程
            if self.output_dicom_path and self.output_nifti_path:
                # DICOM 重新命名 + 轉換為 NIfTI
                self._run_dicom_to_nifti_conversion(executor)
            elif self.output_dicom_path and not self.output_nifti_path:
                # 僅 DICOM 重新命名
                self._run_dicom_rename_only(executor)
            elif not self.output_dicom_path and self.output_nifti_path:
                # 假設輸入是已重新命名的 DICOM，轉換為 NIfTI
                self._run_dicom_to_nifti_conversion(executor)
            else:
                raise ProcessingError(
                    "必須提供至少一個輸出路徑 (output_dicom 或 output_nifti)"
                )

            end_time = time.time()
            self._log_progress(f"轉換完成，耗時: {end_time - start_time:.2f} 秒")

        except Exception as e:
            raise ProcessingError(f"轉換管理器執行失敗: {str(e)}")

    def _run_dicom_to_nifti_conversion(self, executor: ExecutorType) -> None:
        """執行 DICOM 到 NIfTI 轉換流程 - 包含完整的重新命名步驟"""
        try:
            self._log_progress("開始 DICOM 到 NIfTI 轉換流程")

            # 步驟 1: 如果有 output_dicom_path，先執行 DICOM 重新命名
            dicom_source_path = self.input_path
            if self.output_dicom_path:
                self._log_progress("步驟 1: 執行 DICOM 重新命名")

                from .dicom_rename_manager import DicomRenameManager

                dicom_rename_manager = DicomRenameManager(
                    input_path=self.input_path, output_path=self.output_dicom_path
                )

                if executor:
                    dicom_rename_manager.run(executor)
                else:
                    with self._create_executor(self.worker_count) as rename_executor:
                        dicom_rename_manager.run(rename_executor)

                # 更新源路徑為重新命名後的 DICOM 路徑
                dicom_source_path = self.output_dicom_path

                # 生成 DICOM 報告
                generate_study_report(self.output_dicom_path)
                self._log_progress("DICOM 重新命名完成")

            # 步驟 2: 執行 DICOM 到 NIfTI 轉換
            self._log_progress("步驟 2: 執行 DICOM 到 NIfTI 轉換")

            if not self._dicom_to_nifti_converter:
                self._dicom_to_nifti_converter = DicomToNiftiConverter(
                    str(dicom_source_path), str(self.output_nifti_path)
                )

            # 執行轉換
            if executor:
                self._dicom_to_nifti_converter.convert(executor)
            else:
                with self._create_executor(self.worker_count) as conv_executor:
                    self._dicom_to_nifti_converter.convert(conv_executor)

            # 步驟 3: 生成 NIfTI 報告
            if self.output_nifti_path:
                generate_nifti_report(self.output_nifti_path)

            # 步驟 4: 執行 NIfTI 後處理
            self._run_nifti_postprocessing()

            self._log_progress("DICOM 到 NIfTI 轉換流程完成")

        except Exception as e:
            raise ProcessingError(f"DICOM 到 NIfTI 轉換失敗: {str(e)}")

    def _run_dicom_rename_only(self, executor: ExecutorType) -> None:
        """執行僅 DICOM 重新命名流程 - 使用正確的重新命名邏輯"""
        try:
            self._log_progress("開始 DICOM 重新命名")

            # 使用專門的 DICOM 重新命名管理器
            from .dicom_rename_manager import DicomRenameManager

            dicom_rename_manager = DicomRenameManager(
                input_path=self.input_path, output_path=self.output_dicom_path
            )

            # 執行重新命名
            if executor:
                dicom_rename_manager.run(executor)
            else:
                with self._create_executor(self.worker_count) as rename_executor:
                    dicom_rename_manager.run(rename_executor)

            # 生成報告
            if self.output_dicom_path and self.output_dicom_path.exists():
                from ..utils.reporting import generate_study_report

                generate_study_report(self.output_dicom_path)

            self._log_progress("DICOM 重新命名完成")

        except Exception as e:
            raise ProcessingError(f"DICOM 重新命名失敗: {str(e)}")

    def _run_nifti_to_dicom_conversion(self, executor: ExecutorType) -> None:
        """執行 NIfTI 到 DICOM 轉換流程"""
        try:
            self._log_progress("開始 NIfTI 到 DICOM 轉換")

            # 建立轉換器
            if not self._nifti_to_dicom_converter:
                self._nifti_to_dicom_converter = NiftiToDicomConverter(
                    str(self.input_path), str(self.output_dicom_path)
                )

            # 執行轉換
            if executor:
                self._nifti_to_dicom_converter.convert(executor)
            else:
                with self._create_executor(self.worker_count) as conv_executor:
                    self._nifti_to_dicom_converter.convert(conv_executor)

            # 生成報告
            if self.output_dicom_path:
                generate_study_report(self.output_dicom_path)

            self._log_progress("NIfTI 到 DICOM 轉換完成")

        except Exception as e:
            raise ProcessingError(f"NIfTI 到 DICOM 轉換失敗: {str(e)}")

    def _run_nifti_postprocessing(self) -> None:
        """執行 NIfTI 後處理"""
        try:
            if not self.output_nifti_path:
                return

            self._log_progress("開始 NIfTI 後處理")

            if not self._nifti_postprocessor:
                self._nifti_postprocessor = NiftiPostProcessManager(
                    self.output_nifti_path
                )

            self._nifti_postprocessor.run()

            self._log_progress("NIfTI 後處理完成")

        except Exception as e:
            raise ProcessingError(f"NIfTI 後處理失敗: {str(e)}")

    def get_conversion_statistics(self) -> dict:
        """獲取轉換統計資訊"""
        stats = {}

        try:
            if self._dicom_to_nifti_converter:
                stats["dicom_to_nifti"] = (
                    self._dicom_to_nifti_converter.get_conversion_statistics()
                )

            # 添加其他統計資訊
            if self.output_nifti_path and self.output_nifti_path.exists():
                nifti_files = list(self.output_nifti_path.rglob("*.nii.gz"))
                stats["total_nifti_files"] = len(nifti_files)

            if self.output_dicom_path and self.output_dicom_path.exists():
                dicom_files = list(self.output_dicom_path.rglob("*.dcm"))
                stats["total_output_dicom_files"] = len(dicom_files)

            return stats

        except Exception as e:
            self._handle_processing_error(e, "獲取轉換統計")
            return {}
