"""
ADC 處理策略模組 - 遵循 .cursor 規則
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
    ImageOrientationEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import (
    ImageOrientationProcessingStrategy,
    MRRenameSeriesProcessingStrategy,
)


class ADCProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """ADC 處理策略"""

    type_2d_series_rename_mapping = {
        MRSeriesRenameEnum.ADC: re.compile(".*(ADC).*", re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
    )

    type_2d_series_rename_dict = {
        MRSeriesRenameEnum.ADC: {
            MRSeriesRenameEnum.ADC,
            ImageOrientationEnum.AXI,
        },
    }

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()

    @classmethod
    def get_image_orientation(
        cls, dicom_ds: DicomDataset
    ) -> Union[BaseEnum, ImageOrientationEnum]:
        """獲取影像方向資訊，包含 REFORMATTED 檢查 - 遵循 .cursor 規則"""
        # Early Return 模式 - 檢查必要標籤
        image_orientation = cls.image_orientation_processing_strategy.process(
            dicom_ds=dicom_ds
        )
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type or len(image_type.value) < 3:
            return image_orientation

        # 檢查是否為 REFORMATTED 影像
        is_reformatted = image_type.value[2] == "REFORMATTED"

        if is_reformatted:
            # 根據原始方向返回重新格式化的方向
            reformatted_mapping = {
                ImageOrientationEnum.AXI: ImageOrientationEnum.AXIr,
                ImageOrientationEnum.SAG: ImageOrientationEnum.SAGr,
                ImageOrientationEnum.COR: ImageOrientationEnum.CORr,
            }
            return reformatted_mapping.get(image_orientation, image_orientation)

        return image_orientation

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 ADC 序列"""
        try:
            # 檢查模態
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            # 檢查 MR 獲取類型
            mr_acquisition_type_enum = (
                self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            )
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 處理序列描述
            series_description = dicom_ds.get((0x08, 0x103E))
            if not series_description:
                return NullEnum.NULL

            # 檢查是否匹配 ADC 模式
            for series_enum, pattern in self.type_2d_series_rename_mapping.items():
                if pattern.search(series_description.value):
                    # 獲取影像方向
                    image_orientation = self.get_image_orientation(dicom_ds)

                    # 匹配重新命名字典
                    for (
                        rename_enum,
                        required_set,
                    ) in self.type_2d_series_rename_dict.items():
                        if {series_enum, image_orientation}.issubset(required_set):
                            return rename_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"ADC 處理失敗: {str(e)}", details={"dicom_ds": dicom_ds}
            ) from e


class EADCProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """Enhanced ADC 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.eADC: re.compile(".*(eADC).*", re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum, NullEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
        NullEnum.NULL,
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 Enhanced ADC 序列 - 使用 Early Return 模式"""
        try:
            # Guard Clauses - Early Return 模式
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            series_description = dicom_ds.get((0x08, 0x103E))
            if not series_description:
                return NullEnum.NULL

            # 檢查序列描述匹配
            for series_enum, pattern in self.series_rename_mapping.items():
                if pattern.match(series_description.value):
                    return series_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"eADC 處理失敗: {str(e)}", processing_stage="eadc_processing"
            ) from e
