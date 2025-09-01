"""
額外的 DICOM 處理策略實作 - 遵循 .cursor 規則
"""

import re
from typing import Union

from ...core.enums import (
    BaseEnum,
    BodyPartEnum,
    DTISeriesEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
    RepetitionTimeEnum,
)
from ...core.exceptions import ProcessingError
from ...core.types import DicomDataset
from ..base import MRRenameSeriesProcessingStrategy


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
            )


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
            )


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
            )


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
            )


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
            )


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
