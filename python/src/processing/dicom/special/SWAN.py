"""
SWAN 處理策略模組 - 遵循 .cursor 規則
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
    SeriesEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import (
    ImageOrientationProcessingStrategy,
    MRRenameSeriesProcessingStrategy,
)


class SWANProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """SWAN 處理策略"""

    type_2d_series_rename_mapping = {
        MRSeriesRenameEnum.SWAN: re.compile(".*(SWAN).*", re.IGNORECASE),
    }

    type_3d_series_rename_mapping = {
        MRSeriesRenameEnum.SWAN: re.compile(".*(SWAN).*", re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    # 重新命名字典
    type_2d_series_rename_dict = {
        MRSeriesRenameEnum.SWAN: {
            MRSeriesRenameEnum.SWAN,
            ImageOrientationEnum.AXI,
            SeriesEnum.ORIGINAL,
        },
        MRSeriesRenameEnum.SWANmIP: {
            MRSeriesRenameEnum.SWAN,
            ImageOrientationEnum.AXI,
            SeriesEnum.mIP,
        },
        MRSeriesRenameEnum.SWANPHASE: {
            MRSeriesRenameEnum.SWAN,
            ImageOrientationEnum.AXI,
            SeriesEnum.SWANPHASE,
        },
    }

    type_3d_series_rename_dict = {
        MRSeriesRenameEnum.SWAN: {
            MRSeriesRenameEnum.SWAN,
            ImageOrientationEnum.AXI,
            SeriesEnum.ORIGINAL,
        },
        MRSeriesRenameEnum.SWANmIP: {
            MRSeriesRenameEnum.SWAN,
            ImageOrientationEnum.AXI,
            SeriesEnum.mIP,
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

    @classmethod
    def get_series_type(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, NullEnum]:
        """獲取序列類型"""
        try:
            image_type = dicom_ds.get((0x08, 0x08))
            if not image_type:
                return NullEnum.NULL

            image_type_values = image_type.value

            if len(image_type_values) >= 3:
                if "ORIGINAL" in image_type_values and "PRIMARY" in image_type_values:
                    return SeriesEnum.ORIGINAL
                elif "DERIVED" in image_type_values:
                    series_description = dicom_ds.get((0x08, 0x103E))
                    if series_description:
                        desc = series_description.value.upper()
                        if "MIP" in desc:
                            return SeriesEnum.mIP
                        elif "PHASE" in desc:
                            return SeriesEnum.SWANPHASE

            return NullEnum.NULL

        except Exception:
            return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 SWAN 序列"""
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

            # 根據獲取類型選擇處理方式
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_type(
                    dicom_ds,
                    self.type_2d_series_rename_mapping,
                    self.type_2d_series_rename_dict,
                )
            elif mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_3D:
                return self._process_type(
                    dicom_ds,
                    self.type_3d_series_rename_mapping,
                    self.type_3d_series_rename_dict,
                )

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"SWAN 處理失敗: {str(e)}", details={"dicom_ds": dicom_ds}
            ) from e

    def _process_type(
        self, dicom_ds: DicomDataset, series_mapping: dict, rename_dict: dict
    ) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理特定類型的序列"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        # 檢查序列描述是否匹配
        for series_enum, pattern in series_mapping.items():
            if pattern.search(series_description.value):
                # 獲取序列分組資訊
                group_results = {
                    series_enum,
                    self.get_image_orientation(dicom_ds),
                    self.get_series_type(dicom_ds),
                }

                # 移除 NULL 值
                group_results.discard(NullEnum.NULL)

                # 匹配重新命名字典
                for rename_enum, required_set in rename_dict.items():
                    if required_set.issubset(group_results):
                        return rename_enum

        return NullEnum.NULL
