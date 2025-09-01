"""
Resting State 處理策略模組 - 遵循 .cursor 規則
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
    RepetitionTimeEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy
from .CVR import CVRProcessingStrategy


class RestingProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """Resting State 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.RESTING: re.compile(".*(Resting|REST).*$", re.IGNORECASE),
    }

    type_2d_series_rename_dict = {
        MRSeriesRenameEnum.RESTING2000: {
            MRSeriesRenameEnum.RESTING,
            RepetitionTimeEnum.TR2000,
        },
        MRSeriesRenameEnum.RESTING: {MRSeriesRenameEnum.RESTING},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
    )

    @classmethod
    def get_repetition_time(
        cls, dicom_ds: DicomDataset
    ) -> Union[RepetitionTimeEnum, NullEnum]:
        """獲取重複時間資訊 - 重用 CVR 的邏輯"""
        return CVRProcessingStrategy.get_repetition_time(dicom_ds)

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 Resting State 序列"""
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

            # 檢查 Resting 模式
            for series_enum, pattern in self.series_rename_mapping.items():
                if pattern.match(series_description.value):
                    # 建立分組結果集合
                    group_results = {
                        series_enum,
                        self.get_repetition_time(dicom_ds),
                    }

                    # 移除 NULL 值
                    group_results.discard(NullEnum.NULL)

                    # 匹配重新命名字典
                    for (
                        rename_enum,
                        required_set,
                    ) in self.type_2d_series_rename_dict.items():
                        if required_set.issubset(group_results):
                            return rename_enum

                    # 如果沒有匹配到具體的，返回基本的 RESTING
                    return series_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"Resting 處理失敗: {str(e)}", processing_stage="resting_processing"
            ) from e
