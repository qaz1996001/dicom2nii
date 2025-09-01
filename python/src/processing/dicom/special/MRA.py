"""
MRA 處理策略模組 - 遵循 .cursor 規則
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
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.processing.base import MRRenameSeriesProcessingStrategy


class MRABrainProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """MRA Brain 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.MRA_BRAIN: re.compile(
            ".+(TOF)(((?!Neck).)*)$", re.IGNORECASE
        ),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 MRA Brain 序列"""
        try:
            # Guard Clauses - Early Return 模式
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

            # 檢查 TOF 模式且不包含 Neck
            pattern = self.series_rename_mapping[MRSeriesRenameEnum.MRA_BRAIN]
            match_result = pattern.match(series_description.value)

            if match_result:
                # 檢查影像類型是否為 ORIGINAL
                image_type = dicom_ds.get((0x08, 0x08))
                if (
                    image_type
                    and len(image_type.value) > 0
                    and image_type.value[0] == "ORIGINAL"
                ):
                    return MRSeriesRenameEnum.MRA_BRAIN

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"MRA Brain 處理失敗: {str(e)}", processing_stage="mra_brain_processing"
            ) from e


class MRANeckProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """MRA Neck 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.MRA_NECK: re.compile(".+(TOF).*(Neck).*$", re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 MRA Neck 序列"""
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

            # 檢查 TOF 且包含 Neck 模式
            pattern = self.series_rename_mapping[MRSeriesRenameEnum.MRA_NECK]
            match_result = pattern.match(series_description.value)

            if match_result:
                # 檢查影像類型是否為 ORIGINAL
                image_type = dicom_ds.get((0x08, 0x08))
                if (
                    image_type
                    and len(image_type.value) > 0
                    and image_type.value[0] == "ORIGINAL"
                ):
                    return MRSeriesRenameEnum.MRA_NECK

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"MRA Neck 處理失敗: {str(e)}", processing_stage="mra_neck_processing"
            ) from e


class MRAVRBrainProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """MRA VR Brain 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.MRAVR_BRAIN: re.compile(
            "((?!TOF|Neck).)*(MRA)((?!Neck).)*$", re.IGNORECASE
        ),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 MRA VR Brain 序列"""
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

            # 檢查 MRA 但不包含 TOF 或 Neck
            pattern = self.series_rename_mapping[MRSeriesRenameEnum.MRAVR_BRAIN]
            match_result = pattern.match(series_description.value)

            if match_result:
                return MRSeriesRenameEnum.MRAVR_BRAIN

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"MRA VR Brain 處理失敗: {str(e)}",
                processing_stage="mravr_brain_processing",
            ) from e


class MRAVRNeckProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """MRA VR Neck 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.MRAVR_NECK: re.compile(
            "((?!TOF).)*(Neck.*MRA)|(MRA.*Neck).*$", re.IGNORECASE
        ),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 MRA VR Neck 序列"""
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

            # 檢查包含 Neck 和 MRA 但不包含 TOF
            pattern = self.series_rename_mapping[MRSeriesRenameEnum.MRAVR_NECK]
            match_result = pattern.match(series_description.value)

            if match_result:
                return MRSeriesRenameEnum.MRAVR_NECK

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(
                f"MRA VR Neck 處理失敗: {str(e)}",
                processing_stage="mravr_neck_processing",
            ) from e
