"""
DWI 處理策略模組 - 遵循 .cursor 規則
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
from src.utils.dicom_utils import get_b_values
from src.processing.base import (
    ImageOrientationProcessingStrategy,
    MRRenameSeriesProcessingStrategy,
)


class DwiProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """DWI 處理策略"""

    # 2D 序列重新命名映射
    type_2d_series_rename_mapping = {
        MRSeriesRenameEnum.DWI: re.compile(".*(DWI|AUTODIFF).*", re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
    )

    # 2D 序列重新命名字典
    type_2d_series_rename_dict = {
        MRSeriesRenameEnum.DWI0: {
            MRSeriesRenameEnum.DWI,
            MRSeriesRenameEnum.B_VALUES_0,
            ImageOrientationEnum.AXI,
        },
        MRSeriesRenameEnum.DWI1000: {
            MRSeriesRenameEnum.DWI,
            MRSeriesRenameEnum.B_VALUES_1000,
            ImageOrientationEnum.AXI,
        },
    }

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()
    series_group_fn_list: list = []

    @classmethod
    def get_series_group_fn_list(cls) -> list:
        """獲取序列分組函數列表"""
        if not cls.series_group_fn_list:
            cls.series_group_fn_list.extend(
                [cls.get_image_orientation, cls.get_b_values]
            )
        return cls.series_group_fn_list

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
    def get_b_values(
        cls, dicom_ds: DicomDataset
    ) -> Union[MRSeriesRenameEnum, NullEnum]:
        """獲取 b 值資訊"""
        b_value = get_b_values(dicom_ds)

        if b_value is not None:
            if b_value == int(MRSeriesRenameEnum.B_VALUES_0.value):
                return MRSeriesRenameEnum.B_VALUES_0
            elif b_value == int(MRSeriesRenameEnum.B_VALUES_1000.value):
                return MRSeriesRenameEnum.B_VALUES_1000

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 DWI 序列"""
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

            # 根據獲取類型處理
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_2d_type(dicom_ds)

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"DWI 處理失敗: {str(e)}", details={"dicom_ds": dicom_ds}
            )

    def _process_2d_type(
        self, dicom_ds: DicomDataset
    ) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 2D 類型的 DWI"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        # 檢查序列描述是否匹配 DWI 模式
        for _series_enum, pattern in self.type_2d_series_rename_mapping.items():
            if pattern.search(series_description.value):
                # 獲取序列分組資訊
                group_results = set()
                for group_fn in self.get_series_group_fn_list():
                    result = group_fn(dicom_ds)
                    if result != NullEnum.NULL:
                        group_results.add(result)

                # 匹配重新命名字典
                for (
                    rename_enum,
                    required_set,
                ) in self.type_2d_series_rename_dict.items():
                    if required_set.issubset(group_results):
                        return rename_enum

        return NullEnum.NULL
