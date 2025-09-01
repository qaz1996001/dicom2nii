"""
DTI 處理策略模組 - 遵循 .cursor 規則
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
    DTISeriesEnum
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy


class DTIProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """DTI (Diffusion Tensor Imaging) 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.DTI32D: re.compile(".*(DTI).*", re.IGNORECASE),
        MRSeriesRenameEnum.DTI64D: re.compile(".*(DTI).*", re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    @classmethod
    def get_dti_directions(
        cls, dicom_ds: DicomDataset
    ) -> Union[DTISeriesEnum, NullEnum]:
        """獲取 DTI 方向數量 - 純函數"""
        # 檢查 DTI 相關的 DICOM 標籤
        series_description = dicom_ds.get((0x08, 0x103E))

        if not series_description:
            return NullEnum.NULL

        desc = series_description.value.upper()

        # 根據描述中的數字判斷方向數
        if "64" in desc:
            return DTISeriesEnum.DTI64D
        elif "32" in desc:
            return DTISeriesEnum.DTI32D

        # 預設返回 32 方向
        return DTISeriesEnum.DTI32D

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 DTI 序列"""
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

            # 檢查 DTI 模式
            if "DTI" in series_description.value.upper():
                dti_directions = self.get_dti_directions(dicom_ds)

                if dti_directions == DTISeriesEnum.DTI32D:
                    return MRSeriesRenameEnum.DTI32D
                elif dti_directions == DTISeriesEnum.DTI64D:
                    return MRSeriesRenameEnum.DTI64D

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"DTI 處理失敗: {str(e)}", processing_stage="dti_processing"
            )
