"""
SWAN NIfTI 處理策略模組 - 遵循 .cursor 規則
"""

import re
from pathlib import Path

from src.core.config import Config
from src.core.exceptions import ProcessingError
from src.processing.base import NiftiProcessingStrategy


class SWANNiftiProcessingStrategy(NiftiProcessingStrategy):
    """SWAN NIfTI 處理策略"""

    pattern = re.compile(r"(?<!e)(SWAN[a-z]{0,2}?)(\.nii\.gz)$", re.IGNORECASE)
    suffix_pattern = re.compile(r"(?<!e)(SWAN)([a-z]{0,2}?)(\.nii\.gz)$", re.IGNORECASE)
    file_size_limit = Config.LARGE_FILE_SIZE_LIMIT  # 800KB

    def process(self, study_path: Path, *args, **kwargs) -> None:
        """處理 SWAN NIfTI 檔案"""
        try:
            self.delete_small_files(study_path)
            self._rename_swan_files(study_path)
        except Exception as e:
            raise ProcessingError(f"SWAN NIfTI 處理失敗: {str(e)}") from e

    def _rename_swan_files(self, study_path: Path) -> None:
        """重新命名 SWAN 檔案"""
        swan_files = []

        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                swan_files.append(series_path)

        for series_path in swan_files:
            if not series_path.exists():
                continue

            if len(swan_files) == 1:
                new_file_path = self.rename_file_without_suffix(
                    series_path, self.suffix_pattern
                )
            else:
                new_file_path = self.rename_file_with_suffix(
                    series_path, self.suffix_pattern
                )

            if new_file_path:
                self.rename_related_files(series_path, new_file_path)
                series_path.rename(new_file_path)
