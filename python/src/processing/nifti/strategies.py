"""
NIfTI 處理策略實作
"""

import re
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np

from ...core.config import Config
from ...core.exceptions import ProcessingError
from ..base import NiftiProcessingStrategy


class DwiNiftiProcessingStrategy(NiftiProcessingStrategy):
    """DWI NIfTI 處理策略"""

    pattern = re.compile(r'(DWI.*)(\.nii\.gz)$')
    suffix_pattern = re.compile(r'(DWI.*)(?<![a-z])([a-z]{0,2}?)(\.nii\.gz)$')
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
                new_file_path = self.rename_file_without_suffix(series_path, self.suffix_pattern)
            else:
                # 多個檔案，添加數字後綴
                new_file_path = self.rename_file_with_suffix(series_path, self.suffix_pattern)

            if new_file_path:
                self.rename_related_files(series_path, new_file_path)
                series_path.rename(new_file_path)


class ADCNiftiProcessingStrategy(NiftiProcessingStrategy):
    """ADC NIfTI 處理策略"""

    pattern = re.compile(r'(?<!e)(ADC[a-z]{0,2}?)(\.nii\.gz)$', re.IGNORECASE)
    suffix_pattern = re.compile(r'(?<!e)(ADC)([a-z]{0,2}?)(\.nii\.gz)$', re.IGNORECASE)
    dwi_pattern = re.compile(r'(DWI0)(.*\.nii\.gz)$', re.IGNORECASE)
    file_size_limit = Config.SMALL_FILE_SIZE_LIMIT  # 100KB

    def process(self, study_path: Path, *args, **kwargs) -> None:
        """處理 ADC NIfTI 檔案"""
        try:
            self._update_adc_headers(study_path)
            self._rename_adc_files(study_path)
        except Exception as e:
            raise ProcessingError(f"ADC NIfTI 處理失敗: {str(e)}")

    def _update_adc_headers(self, study_path: Path) -> None:
        """更新 ADC 檔案的標頭資訊"""
        adc_files = []
        dwi_files = []

        # 收集 ADC 和 DWI 檔案
        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                adc_files.append(series_path.name)
            elif self.dwi_pattern.match(series_path.name):
                dwi_files.append(series_path.name)

        # 如果同時有 DWI 和 ADC 檔案，更新 ADC 的標頭
        if dwi_files and adc_files:
            for dwi_file in dwi_files:
                dwi_nii = nib.load(str(study_path / dwi_file))

                for adc_file in adc_files:
                    adc_path = study_path / adc_file
                    adc_nii = nib.load(str(adc_path))

                    # 檢查形狀是否匹配
                    if dwi_nii.get_fdata().shape == adc_nii.get_fdata().shape:
                        # 更新標頭
                        new_header = adc_nii.header.copy()
                        new_header['pixdim'] = dwi_nii.header['pixdim']
                        new_affine = dwi_nii.affine
                        data = adc_nii.get_fdata()

                        # 儲存更新後的檔案
                        output_nii = nib.Nifti1Image(data, new_affine, new_header)
                        nib.save(output_nii, str(adc_path))

    def _rename_adc_files(self, study_path: Path) -> None:
        """重新命名 ADC 檔案"""
        adc_files = []
        dwi_files = []

        # 收集檔案
        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                adc_files.append(series_path)
            elif self.dwi_pattern.match(series_path.name):
                dwi_files.append(series_path)

        # 處理重新命名
        for adc_path in adc_files:
            if not adc_path.exists():
                continue

            if len(adc_files) == 1:
                # 單一 ADC 檔案
                new_file_path = self.rename_file_without_suffix(adc_path, self.suffix_pattern)
                if new_file_path:
                    self.rename_related_files(adc_path, new_file_path)
                    adc_path.rename(new_file_path)
            else:
                # 多個 ADC 檔案，需要與 DWI 檔案配對
                self._pair_adc_with_dwi(adc_path, dwi_files, study_path)

    def _pair_adc_with_dwi(self, adc_path: Path, dwi_files: list[Path], study_path: Path) -> None:
        """將 ADC 檔案與對應的 DWI 檔案配對"""
        adc_nii = nib.load(str(adc_path))
        data = adc_nii.get_fdata().round(0).astype(np.int32)

        for dwi_file in dwi_files:
            dwi_nii = nib.load(str(dwi_file))

            # 檢查仿射矩陣是否匹配
            if np.array_equal(dwi_nii.affine, adc_nii.affine):
                # 刪除原始 ADC 檔案
                adc_path.unlink()

                # 建立新的 ADC 檔案名稱
                new_adc_name = dwi_file.name.replace('DWI0', 'ADC')
                new_adc_path = adc_path.parent / new_adc_name

                # 儲存新的 ADC 檔案
                output_nii = nib.Nifti1Image(data, adc_nii.affine, adc_nii.header)
                nib.save(output_nii, str(new_adc_path))

                # 處理相關檔案 (bval, bvec)
                self._handle_related_files(adc_path, new_adc_path)
                break

    def _handle_related_files(self, old_path: Path, new_path: Path) -> None:
        """處理相關的 bval 和 bvec 檔案"""
        for suffix in ['.bval', '.bvec']:
            old_related = old_path.parent / (old_path.stem + suffix)
            if old_related.exists():
                new_related = new_path.parent / (new_path.stem + suffix)
                old_related.rename(new_related)


class SWANNiftiProcessingStrategy(NiftiProcessingStrategy):
    """SWAN NIfTI 處理策略"""

    pattern = re.compile(r'(?<!e)(SWAN[a-z]{0,2}?)(\.nii\.gz)$', re.IGNORECASE)
    suffix_pattern = re.compile(r'(?<!e)(SWAN)([a-z]{0,2}?)(\.nii\.gz)$', re.IGNORECASE)
    file_size_limit = Config.LARGE_FILE_SIZE_LIMIT  # 800KB

    def process(self, study_path: Path, *args, **kwargs) -> None:
        """處理 SWAN NIfTI 檔案"""
        try:
            self.delete_small_files(study_path)
            self._rename_swan_files(study_path)
        except Exception as e:
            raise ProcessingError(f"SWAN NIfTI 處理失敗: {str(e)}")

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
                new_file_path = self.rename_file_without_suffix(series_path, self.suffix_pattern)
            else:
                new_file_path = self.rename_file_with_suffix(series_path, self.suffix_pattern)

            if new_file_path:
                self.rename_related_files(series_path, new_file_path)
                series_path.rename(new_file_path)


class T1NiftiProcessingStrategy(NiftiProcessingStrategy):
    """T1 NIfTI 處理策略"""

    pattern = re.compile(r'(T1.*)(\.nii\.gz)$')
    suffix_pattern = re.compile(r'(T1.*)(AXIr?|CORr?|SAGr?)([a-z]{0,1})(\.nii\.gz)$')
    file_size_limit = Config.LARGE_FILE_SIZE_LIMIT  # 800KB

    def process(self, study_path: Path, *args, **kwargs) -> None:
        """處理 T1 NIfTI 檔案"""
        try:
            self.delete_small_files(study_path)
            self._rename_t1_files(study_path)
        except Exception as e:
            raise ProcessingError(f"T1 NIfTI 處理失敗: {str(e)}")

    def _rename_t1_files(self, study_path: Path) -> None:
        """重新命名 T1 檔案"""
        t1_files = []

        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                t1_files.append(series_path)

        for series_path in t1_files:
            if not series_path.exists():
                continue

            if len(t1_files) == 1:
                new_file_path = self._rename_t1_file_without_suffix(series_path)
            else:
                new_file_path = self._rename_t1_file_with_suffix(series_path)

            if new_file_path:
                self.rename_related_files(series_path, new_file_path)
                series_path.rename(new_file_path)

    def _rename_t1_file_with_suffix(self, series_path: Path) -> Optional[Path]:
        """重新命名 T1 檔案並添加後綴"""
        pattern_result = self.suffix_pattern.match(series_path.name)
        if pattern_result:
            groups = pattern_result.groups()
            if len(groups) > 2 and len(groups[2]) > 0:
                suffix_char = groups[2]
                suffix_int = ord(suffix_char) - Config.CHAR_OFFSET
                new_file_name = f'{groups[0]}{groups[1]}_{suffix_int}.nii.gz'
                return series_path.parent / new_file_name
        return None

    def _rename_t1_file_without_suffix(self, series_path: Path) -> Optional[Path]:
        """重新命名 T1 檔案但不添加後綴"""
        pattern_result = self.suffix_pattern.match(series_path.name)
        if pattern_result:
            groups = pattern_result.groups()
            new_file_name = f'{groups[0]}{groups[1]}.nii.gz'
            return series_path.parent / new_file_name
        return None


class T2NiftiProcessingStrategy(NiftiProcessingStrategy):
    """T2 NIfTI 處理策略"""

    pattern = re.compile(r'(T2.*)(\.nii\.gz)$')
    suffix_pattern = re.compile(r'(T2.*)(AXIr?|CORr?|SAGr?)([a-z]{0,1})(\.nii\.gz)$')
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
                new_file_name = f'{groups[0]}{groups[1]}_{suffix_int}.nii.gz'
                return series_path.parent / new_file_name
        return None

    def _rename_t2_file_without_suffix(self, series_path: Path) -> Optional[Path]:
        """重新命名 T2 檔案但不添加後綴"""
        pattern_result = self.suffix_pattern.match(series_path.name)
        if pattern_result:
            groups = pattern_result.groups()
            new_file_name = f'{groups[0]}{groups[1]}.nii.gz'
            return series_path.parent / new_file_name
        return None
