"""
ASL 處理策略模組 - 遵循 .cursor 規則
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
    ASLSEQSeriesRenameEnum,
    BaseEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy


class ASLProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """ASL (Arterial Spin Labeling) 處理策略"""

    # 序列重新命名映射
    series_rename_mapping = {
        ASLSEQSeriesRenameEnum.ASLSEQ: re.compile(
            "(multi-Delay ASL SEQ)", re.IGNORECASE
        ),
        ASLSEQSeriesRenameEnum.ASLPROD: re.compile(
            "(3D ASL [(]non-contrast[)])", re.IGNORECASE
        ),
        ASLSEQSeriesRenameEnum.ASLSEQATT: re.compile(
            "([(]Transit delay[)] multi-Delay ASL SEQ)", re.IGNORECASE
        ),
        ASLSEQSeriesRenameEnum.ASLSEQATT_COLOR: re.compile(
            "([(]Color Transit delay[)] multi-Delay ASL SEQ)", re.IGNORECASE
        ),
        ASLSEQSeriesRenameEnum.ASLSEQCBF: re.compile(
            "([(]Transit corrected CBF[)] multi-Delay ASL SEQ)", re.IGNORECASE
        ),
        ASLSEQSeriesRenameEnum.ASLSEQCBF_COLOR: re.compile(
            "([(]Color Transit corrected CBF[)] multi-Delay ASL SEQ)", re.IGNORECASE
        ),
        ASLSEQSeriesRenameEnum.ASLSEQPW: re.compile(
            "([(]per del, mean PW, REF[)] multi-Delay ASL SEQ)", re.IGNORECASE
        ),
    }

    type_3d_series_rename_mapping = series_rename_mapping
    type_3d_series_rename_dict = {}  # 根據需要填充

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    @classmethod
    def get_asl_info(
        cls, dicom_ds: DicomDataset
    ) -> Union[ASLSEQSeriesRenameEnum, NullEnum]:
        """獲取 ASL 資訊"""
        # 檢查 ASL 標籤
        pulse_sequence_name = dicom_ds.get((0x19, 0x109C))
        if (
            pulse_sequence_name
            and str(pulse_sequence_name.value).lower()
            == ASLSEQSeriesRenameEnum.ASL.value.lower()
        ):
            return ASLSEQSeriesRenameEnum.ASL

        # 檢查 ASL 技術標籤
        asl_technique = dicom_ds.get((0x43, 0x10A4))
        if (
            asl_technique
            and ASLSEQSeriesRenameEnum.ASL.value.lower()
            in str(asl_technique.value).lower()
        ):
            return ASLSEQSeriesRenameEnum.ASL

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 ASL 序列"""
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

            # 檢查序列描述
            series_description = dicom_ds.get((0x08, 0x103E))
            if not series_description:
                return NullEnum.NULL

            # 匹配 ASL 模式
            for series_enum, pattern in self.series_rename_mapping.items():
                if pattern.search(series_description.value):
                    return series_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"ASL 處理失敗: {str(e)}",
                processing_stage="asl_processing",
                details={"dicom_ds": str(dicom_ds)},
            )
