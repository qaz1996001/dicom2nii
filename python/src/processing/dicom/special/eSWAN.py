"""
Enhanced SWAN 處理策略模組 - 遵循 .cursor 規則
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
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
    SeriesEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy


class ESWANProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """Enhanced SWAN 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.eSWAN: re.compile(".*(SWAN).*", re.IGNORECASE),
    }

    series_rename_dict = {
        MRSeriesRenameEnum.eSWAN: {SeriesEnum.eSWAN, SeriesEnum.ORIGINAL},
        MRSeriesRenameEnum.eSWANmIP: {SeriesEnum.eSWAN, SeriesEnum.mIP},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    @classmethod
    def get_mip_info(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, NullEnum]:
        """獲取 mIP 資訊 - 純函數實作"""
        image_type = dicom_ds.get((0x08, 0x08))
        instance_creation_time = dicom_ds.get((0x08, 0x13))

        if not image_type or not instance_creation_time:
            return NullEnum.NULL

        # 檢查是否為 MIN IP 或 REFORMATTED
        is_min_ip = len(image_type.value) > 0 and image_type.value[-1] in [
            "MIN IP",
            "REFORMATTED",
        ]

        return SeriesEnum.mIP if is_min_ip else NullEnum.NULL

    @classmethod
    def get_original_info(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, NullEnum]:
        """獲取 ORIGINAL 資訊 - 純函數實作"""
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type:
            return NullEnum.NULL

        # 檢查是否為 ORIGINAL
        is_original = "ORIGINAL" in image_type.value

        return SeriesEnum.ORIGINAL if is_original else NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 Enhanced SWAN 序列"""
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

            series_description = dicom_ds.get((0x08, 0x103E))
            if not series_description:
                return NullEnum.NULL

            # 檢查序列描述匹配
            for _series_enum, pattern in self.series_rename_mapping.items():
                if pattern.match(series_description.value):
                    # 獲取序列分組資訊
                    group_results = {
                        SeriesEnum.eSWAN,
                        self.get_mip_info(dicom_ds),
                        self.get_original_info(dicom_ds),
                    }

                    # 移除 NULL 值
                    group_results.discard(NullEnum.NULL)

                    # 匹配重新命名字典
                    for rename_enum, required_set in self.series_rename_dict.items():
                        if required_set.issubset(group_results):
                            return rename_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"eSWAN 處理失敗: {str(e)}", processing_stage="eswan_processing"
            ) from e
