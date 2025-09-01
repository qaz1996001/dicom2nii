"""
DICOM 到 NIfTI 轉換器
"""

import re
import subprocess
import traceback
from concurrent.futures import Future
from pathlib import Path

try:
    import dcm2niix
except ImportError:
    dcm2niix = None

from ..core.enums import MRSeriesRenameEnum
from ..core.exceptions import ConversionError
from ..core.types import ExecutorType
from .base import BaseConverter


class DicomToNiftiConverter(BaseConverter):
    """DICOM 到 NIfTI 轉換器"""

    def __init__(self, input_path: str, output_path: str):
        """初始化轉換器

        Args:
            input_path: 輸入 DICOM 路徑
            output_path: 輸出 NIfTI 路徑
        """
        super().__init__(input_path, output_path)

        # 設定預設排除集合
        self.exclude_set = {
            MRSeriesRenameEnum.MRAVR_BRAIN.value,
            MRSeriesRenameEnum.MRAVR_NECK.value,
            # 可以根據需要添加更多排除項目
        }

    def convert(self, executor: ExecutorType = None) -> None:
        """執行 DICOM 到 NIfTI 轉換

        Args:
            executor: 執行器，用於並行處理
        """
        try:
            # 尋找所有 DICOM 檔案
            dicom_instances = list(self.input_path.rglob("*.dcm"))
            if not dicom_instances:
                raise ConversionError(f"在 {self.input_path} 中找不到 DICOM 檔案")

            # 獲取檢查列表
            study_list = list({instance.parent.parent for instance in dicom_instances})

            # 轉換每個檢查
            futures: list[Future] = []

            for study_path in study_list:
                # 複製元資料
                self._copy_metadata(study_path)

                # 獲取序列列表
                series_list = [
                    series_path
                    for series_path in study_path.iterdir()
                    if series_path.is_dir() and series_path.name != ".meta"
                ]

                # 轉換每個序列
                for series_path in series_list:
                    if self._is_excluded(series_path.name):
                        continue

                    output_series_path = self._get_output_series_path(series_path)
                    output_file_path = Path(f"{output_series_path}.nii.gz")

                    # 跳過已存在的檔案
                    if output_file_path.exists():
                        print(f"檔案已存在，跳過: {output_file_path}")
                        continue

                    # 確保輸出目錄存在
                    self._ensure_output_directory(output_file_path)

                    # 提交轉換任務
                    if executor:
                        future = executor.submit(
                            self._convert_series, output_series_path, series_path
                        )
                        futures.append(future)
                    else:
                        self._convert_series(output_series_path, series_path)

            # 等待所有任務完成
            if executor and futures:
                for future in futures:
                    try:
                        future.result()  # 獲取結果，如果有例外會在這裡拋出
                    except Exception as e:
                        traceback.print_exc()
                        print(f"轉換任務失敗: {str(e)}")

        except Exception as e:
            raise ConversionError(f"DICOM 到 NIfTI 轉換失敗: {str(e)}") from e

    def _get_output_series_path(self, series_path: Path) -> Path:
        """獲取輸出序列路徑"""
        # 直接使用檢查名稱和序列名稱構建輸出路徑
        study_name = series_path.parent.name
        return self.output_path / study_name / series_path.name

    def _convert_series(self, output_series_path: Path, series_path: Path) -> str:
        """轉換單一序列

        Args:
            output_series_path: 輸出序列路徑
            series_path: 輸入序列路徑

        Returns:
            轉換結果字串
        """
        try:
            # Early Return - 檢查 dcm2niix 是否可用
            if dcm2niix is None:
                raise ConversionError("dcm2niix 套件未安裝，無法執行轉換")

            output_file_path = Path(f"{output_series_path}.nii.gz")

            # 建構 dcm2niix 命令
            cmd_str = (
                f"{dcm2niix.bin} -z y -f {output_series_path.name} "
                f"-o {output_series_path.parent} {series_path}"
            )

            # 執行轉換命令
            completed_process = subprocess.run(
                cmd_str,
                capture_output=True,
                text=True,
                timeout=300,  # 5分鐘超時
            )

            if completed_process.returncode != 0:
                raise ConversionError(f"dcm2niix 執行失敗: {completed_process.stderr}")

            # 解析輸出結果
            result_str = self._parse_dcm2niix_output(completed_process.stdout)

            # 處理檔案重新命名
            self._handle_output_files(result_str, output_series_path, output_file_path)

            return result_str

        except subprocess.TimeoutExpired as ee:
            raise ConversionError(f"轉換超時: {series_path}") from ee
        except Exception as e:
            raise ConversionError(f"轉換序列失敗 {series_path}: {str(e)}") from e

    def _parse_dcm2niix_output(self, stdout: str) -> str:
        """解析 dcm2niix 輸出"""
        pattern = re.compile(r"DICOM as (.*)\s[(]", flags=re.MULTILINE)
        match_result = pattern.search(stdout)

        if not match_result:
            raise ConversionError("無法解析 dcm2niix 輸出")

        return match_result.groups()[0]

    def _handle_output_files(
        self, result_str: str, output_series_path: Path, expected_output_path: Path
    ) -> None:
        """處理輸出檔案的重新命名"""
        dcm2niix_output_path = Path(f"{result_str}.nii.gz")

        # 如果輸出檔案名稱與預期不同，進行重新命名
        if dcm2niix_output_path.name != expected_output_path.name:
            try:
                # 重新命名 NIfTI 檔案
                if dcm2niix_output_path.exists():
                    dcm2niix_output_path.rename(expected_output_path)

                # 重新命名對應的 JSON 檔案
                dcm2niix_json_path = Path(
                    str(dcm2niix_output_path).replace(".nii.gz", ".json")
                )
                expected_json_path = Path(
                    str(expected_output_path).replace(".nii.gz", ".json")
                )

                if dcm2niix_json_path.exists():
                    dcm2niix_json_path.rename(expected_json_path)

            except FileExistsError:
                print(f"檔案已存在錯誤: {output_series_path}")
            except Exception as e:
                raise ConversionError(f"重新命名輸出檔案失敗: {str(e)}") from e

    def get_conversion_statistics(self) -> dict:
        """獲取轉換統計資訊"""
        try:
            total_dicom_files = len(list(self.input_path.rglob("*.dcm")))
            total_nifti_files = len(list(self.output_path.rglob("*.nii.gz")))

            return {
                "total_dicom_files": total_dicom_files,
                "total_nifti_files": total_nifti_files,
                "conversion_rate": total_nifti_files / total_dicom_files
                if total_dicom_files > 0
                else 0,
            }
        except Exception as e:
            raise ConversionError(f"獲取轉換統計失敗: {str(e)}") from e
