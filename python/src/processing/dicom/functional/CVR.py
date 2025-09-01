"""
CVR 處理策略模組 - 遵循 .cursor 規則
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
    BodyPartEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
    RepetitionTimeEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy


class CVRProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """CVR (Cerebrovascular Reactivity) 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.CVR: re.compile(".*(CVR).*$", re.IGNORECASE),
    }

    # CVR 序列重新命名字典 - 使用宣告式映射
    type_2d_series_rename_dict = {
        MRSeriesRenameEnum.CVR2000_EAR: {
            MRSeriesRenameEnum.CVR,
            RepetitionTimeEnum.TR2000,
            BodyPartEnum.EAR,
        },
        MRSeriesRenameEnum.CVR2000_EYE: {
            MRSeriesRenameEnum.CVR,
            RepetitionTimeEnum.TR2000,
            BodyPartEnum.EYE,
        },
        MRSeriesRenameEnum.CVR2000: {MRSeriesRenameEnum.CVR, RepetitionTimeEnum.TR2000},
        MRSeriesRenameEnum.CVR1000: {MRSeriesRenameEnum.CVR, RepetitionTimeEnum.TR1000},
        MRSeriesRenameEnum.CVR: {MRSeriesRenameEnum.CVR},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
    )

    @classmethod
    def get_repetition_time(
        cls, dicom_ds: DicomDataset
    ) -> Union[RepetitionTimeEnum, NullEnum]:
        """獲取重複時間資訊 - 純函數"""
        repetition_time = dicom_ds.get((0x18, 0x80))

        if not repetition_time:
            return NullEnum.NULL

        # 檢查重複時間值
        tr_value = str(int(float(repetition_time.value)))

        if tr_value == RepetitionTimeEnum.TR1000.value:
            return RepetitionTimeEnum.TR1000
        elif tr_value == RepetitionTimeEnum.TR2000.value:
            return RepetitionTimeEnum.TR2000

        return NullEnum.NULL

    @classmethod
    def get_body_part_from_description(
        cls, dicom_ds: DicomDataset
    ) -> Union[BodyPartEnum, NullEnum]:
        """從描述中獲取身體部位 - 純函數"""
        series_description = dicom_ds.get((0x08, 0x103E))

        if not series_description:
            return NullEnum.NULL

        desc_lower = series_description.value.lower()

        if BodyPartEnum.EYE.value.lower() in desc_lower:
            return BodyPartEnum.EYE
        elif BodyPartEnum.EAR.value.lower() in desc_lower:
            return BodyPartEnum.EAR

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 CVR 序列"""
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

            # 檢查 CVR 模式
            for series_enum, pattern in self.series_rename_mapping.items():
                if pattern.match(series_description.value):
                    # 建立分組結果集合
                    group_results = {
                        series_enum,
                        self.get_repetition_time(dicom_ds),
                        self.get_body_part_from_description(dicom_ds),
                    }

                    # 移除 NULL 值
                    group_results.discard(NullEnum.NULL)

                    # 匹配重新命名字典 (優先級從具體到一般)
                    for rename_enum, required_set in sorted(
                        self.type_2d_series_rename_dict.items(),
                        key=lambda x: len(x[1]),
                        reverse=True,
                    ):
                        if required_set.issubset(group_results):
                            return rename_enum

                    # 如果沒有匹配到具體的，返回基本的 CVR
                    return series_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"CVR 處理失敗: {str(e)}", processing_stage="cvr_processing"
            )
