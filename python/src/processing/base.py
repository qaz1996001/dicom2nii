"""
統一的基礎處理策略類別
"""

import pathlib
import re
from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Optional, Union

import numpy as np

from ..core.config import Config
from ..core.enums import (
    BaseEnum,
    ContrastEnum,
    ImageOrientationEnum,
    ModalityEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
)
from ..core.exceptions import ProcessingError
from ..core.types import DicomDataset


class BaseProcessingStrategy(metaclass=ABCMeta):
    """所有處理策略的基礎類別"""

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """抽象處理方法"""
        pass

    def __call__(self, *args, **kwargs) -> Any:
        """使策略可以直接呼叫"""
        return self.process(*args, **kwargs)


class DicomProcessingStrategy(BaseProcessingStrategy):
    """DICOM 處理策略基類"""

    @abstractmethod
    def process(self, dicom_ds: DicomDataset, input_path: pathlib.Path, output_path: pathlib.Path) -> Any:
        """處理 DICOM 資料集"""
        pass


class NiftiProcessingStrategy(BaseProcessingStrategy):
    """NIfTI 處理策略基類"""

    # 共用的檔案處理屬性
    pattern: Optional[re.Pattern] = None
    suffix_pattern: Optional[re.Pattern] = None
    file_size_limit: int = Config.DEFAULT_FILE_SIZE_LIMIT

    @abstractmethod
    def process(self, study_path: pathlib.Path, *args, **kwargs) -> Any:
        """處理 NIfTI 檔案"""
        pass

    def delete_small_files(self, study_path: pathlib.Path) -> None:
        """刪除小於指定大小的檔案"""
        if not self.pattern:
            return

        for series_path in study_path.iterdir():
            if self.pattern.match(series_path.name):
                if series_path.stat().st_size < self.file_size_limit:
                    print(f'刪除小檔案: {series_path}')

                    # 刪除對應的 JSON 檔案
                    json_file_path = series_path.parent.joinpath(
                        series_path.name.replace('.nii.gz', '.json')
                    )
                    if json_file_path.exists():
                        json_file_path.unlink()

                    # 刪除 NIfTI 檔案
                    if series_path.exists():
                        series_path.unlink()

    def rename_file_with_suffix(self, series_path: pathlib.Path, pattern: re.Pattern) -> Optional[pathlib.Path]:
        """重新命名檔案並添加後綴"""
        pattern_result = pattern.match(series_path.name)
        if not pattern_result:
            return None

        groups = pattern_result.groups()
        if len(groups) > 1 and len(groups[1]) > 0:
            suffix_char = groups[1]
            suffix_int = ord(suffix_char) - Config.CHAR_OFFSET
            new_file_name = f'{groups[0]}_{suffix_int}.nii.gz'
            return series_path.parent.joinpath(new_file_name)
        return None

    def rename_file_without_suffix(self, series_path: pathlib.Path, pattern: re.Pattern) -> Optional[pathlib.Path]:
        """重新命名檔案但不添加後綴"""
        pattern_result = pattern.match(series_path.name)
        if pattern_result:
            new_file_name = f'{pattern_result.groups()[0]}.nii.gz'
            return series_path.parent.joinpath(new_file_name)
        return None

    def rename_related_files(self, old_path: pathlib.Path, new_path: pathlib.Path) -> None:
        """重新命名相關檔案 (JSON, bval, bvec 等)"""
        old_base_name = old_path.name.replace('.nii.gz', '')
        new_base_name = new_path.name.replace('.nii.gz', '')

        # 尋找所有相關檔案
        related_files = list(filter(
            lambda x: x.stem == old_base_name,
            old_path.parent.iterdir()
        ))

        # 重新命名每個相關檔案
        for related_file in related_files:
            if related_file != old_path:  # 避免重複處理主檔案
                new_related_file = new_path.parent.joinpath(
                    f"{new_base_name}{related_file.suffix}"
                )
                related_file.rename(new_related_file)


class SeriesProcessingStrategy(BaseProcessingStrategy):
    """序列處理策略基類"""

    @abstractmethod
    def process(self, dicom_ds: DicomDataset) -> Union[str, BaseEnum]:
        """處理 DICOM 序列"""
        pass


class ModalityProcessingStrategy(SeriesProcessingStrategy):
    """模態處理策略"""

    modality_list = ModalityEnum.to_list()

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, ModalityEnum]:
        """根據模態處理 DICOM 資料集"""
        try:
            modality = dicom_ds.get((0x08, 0x60))

            if modality:
                for modality_enum in self.modality_list:
                    if modality_enum.value == modality.value:
                        return modality_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"模態處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})


class ImageOrientationProcessingStrategy(SeriesProcessingStrategy):
    """影像方向處理策略"""

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, ImageOrientationEnum]:
        """根據影像方向處理 DICOM 資料集"""
        try:
            image_orientation = dicom_ds.get((0x20, 0x37))

            if image_orientation is None:
                return NullEnum.NULL

            # 處理影像方向資訊
            orientation_values = np.round(image_orientation.value).astype(int)
            orientation_abs = np.abs(orientation_values)
            index_sort = np.argsort(orientation_abs)

            # 根據排序的索引判斷平面視圖
            max_idx, second_max_idx = index_sort[-1], index_sort[-2]

            if self._is_coronal_plane(max_idx, second_max_idx):
                return ImageOrientationEnum.COR
            elif self._is_sagittal_plane(max_idx, second_max_idx):
                return ImageOrientationEnum.SAG
            elif self._is_axial_plane(max_idx, second_max_idx):
                return ImageOrientationEnum.AXI

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"影像方向處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})

    def _is_coronal_plane(self, max_idx: int, second_max_idx: int) -> bool:
        """判斷是否為冠狀面"""
        return ((max_idx == 0 and second_max_idx == 5) or
                (max_idx == 5 and second_max_idx == 0))

    def _is_sagittal_plane(self, max_idx: int, second_max_idx: int) -> bool:
        """判斷是否為矢狀面"""
        return ((max_idx == 1 and second_max_idx == 5) or
                (max_idx == 5 and second_max_idx == 1))

    def _is_axial_plane(self, max_idx: int, second_max_idx: int) -> bool:
        """判斷是否為軸狀面"""
        return ((max_idx == 0 and second_max_idx == 4) or
                (max_idx == 4 and second_max_idx == 0))


class ContrastProcessingStrategy(SeriesProcessingStrategy):
    """對比劑處理策略"""

    modality_processing_strategy: ModalityProcessingStrategy = ModalityProcessingStrategy()
    contrast_pattern = re.compile(r'(\+C|C\+)', re.IGNORECASE)

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, ContrastEnum]:
        """根據模態和對比劑處理 DICOM 資料集"""
        try:
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            contrast = dicom_ds.get((0x18, 0x10))
            series_description = dicom_ds.get((0x08, 0x103E))

            if not series_description:
                return NullEnum.NULL

            series_desc_value = series_description.value

            if modality_enum == ModalityEnum.MR:
                # MR 對比劑檢查
                if contrast and len(str(contrast.value)) > 0:
                    return ContrastEnum.CE
                if self.contrast_pattern.search(series_desc_value):
                    return ContrastEnum.CE
                return ContrastEnum.NE

            elif modality_enum == ModalityEnum.CT:
                # CT 對比劑檢查
                return ContrastEnum.CE if contrast else ContrastEnum.NE

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"對比劑處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})


class MRAcquisitionTypeProcessingStrategy(SeriesProcessingStrategy):
    """MR 獲取類型處理策略"""

    mr_acquisition_type_list: list[MRAcquisitionTypeEnum] = MRAcquisitionTypeEnum.to_list()

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRAcquisitionTypeEnum]:
        """根據 MR 獲取類型處理 DICOM 資料集"""
        try:
            mr_acquisition_type = dicom_ds.get((0x18, 0x23))

            if mr_acquisition_type:
                for acquisition_type_enum in self.mr_acquisition_type_list:
                    if acquisition_type_enum.value == mr_acquisition_type.value:
                        return acquisition_type_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"MR 獲取類型處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})


class MRRenameSeriesProcessingStrategy(SeriesProcessingStrategy, ABC):
    """MR 序列重新命名處理策略抽象基類"""

    modality: ModalityEnum = ModalityEnum.MR
    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum, NullEnum], ...] = tuple(MRAcquisitionTypeEnum.to_list())

    # 策略實例
    modality_processing_strategy: ModalityProcessingStrategy = ModalityProcessingStrategy()
    mr_acquisition_type_processing_strategy: MRAcquisitionTypeProcessingStrategy = MRAcquisitionTypeProcessingStrategy()

    @abstractmethod
    def process(self, dicom_ds: DicomDataset) -> Union[MRSeriesRenameEnum, NullEnum]:
        """抽象方法：處理和重新命名 MR 序列"""
        pass


class CTRenameSeriesProcessingStrategy(SeriesProcessingStrategy, ABC):
    """CT 序列重新命名處理策略抽象基類"""

    modality: ModalityEnum = ModalityEnum.CT
    modality_processing_strategy: ModalityProcessingStrategy = ModalityProcessingStrategy()

    @abstractmethod
    def process(self, dicom_ds: DicomDataset) -> Union[MRSeriesRenameEnum, NullEnum]:
        """抽象方法：處理和重新命名 CT 序列"""
        pass
