"""
T2 NIfTI 處理策略模組 - 遵循 .cursor 規則
"""

import re
from pathlib import Path
from typing import Optional

from src.core.config import Config
from src.core.exceptions import ProcessingError
from src.processing.base import NiftiProcessingStrategy


class T2NiftiProcessingStrategy(NiftiProcessingStrategy):
    """T2 NIfTI 處理策略"""

    pattern = re.compile(r"(T2.*)(\.nii\.gz)$")
    suffix_pattern = re.compile(r"(T2.*)(AXIr?|CORr?|SAGr?)([a-z]{0,1})(\.nii\.gz)$")
    file_size_limit = Config.LARGE_FILE_SIZE_LIMIT  # 800KB

    def process(self, study_path: Path, *args, **kwargs) -> None:
        """處理 T2 NIfTI 檔案"""
        try:
            self.delete_small_files(study_path)
            self._rename_t2_files(study_path)
        except Exception as e:
            raise ProcessingError(f"T2 NIfTI 處理失敗: {str(e)}")

    def _rename_t2_files(self, study_path: Path) -> None:
        """重新命名 T2 檔案"""
        t2_files = []

        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                t2_files.append(series_path)

        for series_path in t2_files:
            if not series_path.exists():
                continue

            if len(t2_files) == 1:
                new_file_path = self._rename_t2_file_without_suffix(series_path)
            else:
                new_file_path = self._rename_t2_file_with_suffix(series_path)

            if new_file_path:
                self.rename_related_files(series_path, new_file_path)
                series_path.rename(new_file_path)

    def _rename_t2_file_with_suffix(self, series_path: Path) -> Optional[Path]:
        """重新命名 T2 檔案並添加後綴"""
        pattern_result = self.suffix_pattern.match(series_path.name)
        if pattern_result:
            groups = pattern_result.groups()
            if len(groups) > 2 and len(groups[2]) > 0:
                suffix_char = groups[2]
                suffix_int = ord(suffix_char) - Config.CHAR_OFFSET
                new_file_name = f"{groups[0]}{groups[1]}_{suffix_int}.nii.gz"
                return series_path.parent / new_file_name
        return None

    def _rename_t2_file_without_suffix(self, series_path: Path) -> Optional[Path]:
        """重新命名 T2 檔案但不添加後綴"""
        pattern_result = self.suffix_pattern.match(series_path.name)
        if pattern_result:
            groups = pattern_result.groups()
            new_file_name = f"{groups[0]}{groups[1]}.nii.gz"
            return series_path.parent / new_file_name
        return None
