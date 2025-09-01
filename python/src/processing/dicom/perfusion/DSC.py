"""
DSC 處理策略模組 - 遵循 .cursor 規則
"""

import re
from typing import Union

try:
    from pydicom import FileDataset
except ImportError:
    # 如果 pydicom 未安裝，定義空的類別
    class FileDataset:
        pass


from src.core.enums import (
    BaseEnum,
    DSCSeriesRenameEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy


class DSCProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """DSC (Dynamic Susceptibility Contrast) 處理策略"""

    # 序列重新命名映射
    series_rename_mapping = {
        DSCSeriesRenameEnum.DSC: re.compile(".*(AUTOPWI|Perfusion).*", re.IGNORECASE),
        DSCSeriesRenameEnum.rCBF: re.compile(".*(CBF).*", re.IGNORECASE),
        DSCSeriesRenameEnum.rCBV: re.compile(".*(CBV).*", re.IGNORECASE),
        DSCSeriesRenameEnum.MTT: re.compile(".*(MTT).*", re.IGNORECASE),
    }

    type_2d_series_rename_mapping = {
        DSCSeriesRenameEnum.DSC: re.compile(".*(AUTOPWI|Perfusion).*", re.IGNORECASE),
    }

    type_null_series_rename_mapping = {
        DSCSeriesRenameEnum.rCBF: re.compile(".*(CBF).*", re.IGNORECASE),
        DSCSeriesRenameEnum.rCBV: re.compile(".*(CBV).*", re.IGNORECASE),
        DSCSeriesRenameEnum.MTT: re.compile(".*(MTT).*", re.IGNORECASE),
    }

    type_null_series_rename_dict = {
        DSCSeriesRenameEnum.rCBF: {DSCSeriesRenameEnum.rCBF},
        DSCSeriesRenameEnum.rCBV: {DSCSeriesRenameEnum.rCBV},
        DSCSeriesRenameEnum.MTT: {DSCSeriesRenameEnum.MTT},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum, NullEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        NullEnum.NULL,
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 DSC 序列"""
        try:
            # Guard Clauses
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            mr_acquisition_type_enum = (
                self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            )
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 根據獲取類型處理
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_type(
                    dicom_ds, self.type_2d_series_rename_mapping, {}
                )
            elif mr_acquisition_type_enum == NullEnum.NULL:
                return self._process_type(
                    dicom_ds,
                    self.type_null_series_rename_mapping,
                    self.type_null_series_rename_dict,
                )

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"DSC 處理失敗: {str(e)}",
                processing_stage="dsc_processing",
                details={"dicom_ds": dicom_ds},
            ) from e

    def _process_type(
        self, dicom_ds: DicomDataset, series_mapping: dict, rename_dict: dict
    ) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理特定類型的 DSC 序列"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        # 檢查序列描述是否匹配
        for series_enum, pattern in series_mapping.items():
            if pattern.search(series_description.value):
                # 如果沒有重新命名字典，直接返回匹配的枚舉
                if not rename_dict:
                    return series_enum

                # 否則檢查重新命名字典
                for rename_enum, required_set in rename_dict.items():
                    if {series_enum}.issubset(required_set):
                        return rename_enum

        return NullEnum.NULL
