"""
DWI NIfTI 處理策略模組 - 遵循 .cursor 規則
"""

import re
from pathlib import Path

from src.core.config import Config
from src.core.exceptions import ProcessingError
from src.processing.base import NiftiProcessingStrategy


class DwiNiftiProcessingStrategy(NiftiProcessingStrategy):
    """DWI NIfTI 處理策略"""

    pattern = re.compile(r"(DWI.*)(\.nii\.gz)$")
    suffix_pattern = re.compile(r"(DWI.*)(?<![a-z])([a-z]{0,2}?)(\.nii\.gz)$")
    file_size_limit = Config.MEDIUM_FILE_SIZE_LIMIT  # 550KB

    def process(self, study_path: Path, *args, **kwargs) -> None:
        """處理 DWI NIfTI 檔案"""
        try:
            self.delete_small_files(study_path)
            self._rename_dwi_files(study_path)
        except Exception as e:
            raise ProcessingError(f"DWI NIfTI 處理失敗: {str(e)}")

    def _rename_dwi_files(self, study_path: Path) -> None:
        """重新命名 DWI 檔案"""
        dwi_files = []

        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                dwi_files.append(series_path)

        for series_path in dwi_files:
            if not series_path.exists():
                continue

            if len(dwi_files) == 1:
                # 單一檔案，移除後綴
                new_file_path = self.rename_file_without_suffix(
                    series_path, self.suffix_pattern
                )
            else:
                # 多個檔案，添加數字後綴
                new_file_path = self.rename_file_with_suffix(
                    series_path, self.suffix_pattern
                )

            if new_file_path:
                self.rename_related_files(series_path, new_file_path)
                series_path.rename(new_file_path)
