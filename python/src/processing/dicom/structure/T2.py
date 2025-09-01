"""
T2 處理策略模組 - 遵循 .cursor 規則
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
    ContrastEnum,
    ImageOrientationEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
    SeriesEnum,
    T2SeriesRenameEnum,
)
from src.core.exceptions import ProcessingError
from src.core.types import DicomDataset
from src.utils.functional_helpers import (
    ProcessingRequest,
    create_attribute_extractor_list,
    process_series_with_type_mapping,
)
from src.processing.base import (
    ContrastProcessingStrategy,
    ImageOrientationProcessingStrategy,
    MRRenameSeriesProcessingStrategy,
)


class T2ProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """T2 處理策略 - 完整實作"""

    # 序列重新命名映射
    series_rename_mapping = {
        T2SeriesRenameEnum.T2: re.compile(".*(T2).*", re.IGNORECASE),
        SeriesEnum.FLAIR: re.compile("(FLAIR)", re.IGNORECASE),
        SeriesEnum.CUBE: re.compile(".*(CUBE).*", re.IGNORECASE),
    }

    type_3d_series_rename_mapping = series_rename_mapping
    type_2d_series_rename_mapping = {
        T2SeriesRenameEnum.T2: re.compile(".*(T2).*", re.IGNORECASE),
        SeriesEnum.FLAIR: re.compile("(FLAIR)", re.IGNORECASE),
    }

    # 2D 序列重新命名字典
    type_2d_series_rename_dict = {
        T2SeriesRenameEnum.T2_AXI: {
            T2SeriesRenameEnum.T2,
            ImageOrientationEnum.AXI,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2_SAG: {
            T2SeriesRenameEnum.T2,
            ImageOrientationEnum.SAG,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2_COR: {
            T2SeriesRenameEnum.T2,
            ImageOrientationEnum.COR,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2CE_AXI: {
            T2SeriesRenameEnum.T2,
            ImageOrientationEnum.AXI,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2CE_SAG: {
            T2SeriesRenameEnum.T2,
            ImageOrientationEnum.SAG,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2CE_COR: {
            T2SeriesRenameEnum.T2,
            ImageOrientationEnum.COR,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2FLAIR_AXI: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            ImageOrientationEnum.AXI,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2FLAIR_SAG: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            ImageOrientationEnum.SAG,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2FLAIR_COR: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            ImageOrientationEnum.COR,
            ContrastEnum.NE,
        },
    }

    # 3D 序列重新命名字典 (完整版，包含 REFORMATTED)
    type_3d_series_rename_dict = {
        # ORIGINAL/PRIMARY T2 CUBE
        T2SeriesRenameEnum.T2CUBE_AXI: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXI,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2CUBE_SAG: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAG,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2CUBE_COR: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.COR,
            ContrastEnum.NE,
        },
        # REFORMATTED T2 CUBE
        T2SeriesRenameEnum.T2CUBE_AXIr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXIr,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2CUBE_SAGr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAGr,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2CUBE_CORr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.CORr,
            ContrastEnum.NE,
        },
        # ORIGINAL/PRIMARY T2 CUBE with Contrast
        T2SeriesRenameEnum.T2CUBECE_AXI: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXI,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2CUBECE_SAG: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAG,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2CUBECE_COR: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.COR,
            ContrastEnum.CE,
        },
        # REFORMATTED T2 CUBE with Contrast
        T2SeriesRenameEnum.T2CUBECE_AXIr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXIr,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2CUBECE_SAGr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAGr,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2CUBECE_CORr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.CUBE,
            ImageOrientationEnum.CORr,
            ContrastEnum.CE,
        },
        # ORIGINAL/PRIMARY T2 FLAIR CUBE
        T2SeriesRenameEnum.T2FLAIRCUBE_AXI: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXI,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2FLAIRCUBE_SAG: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAG,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2FLAIRCUBE_COR: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.COR,
            ContrastEnum.NE,
        },
        # REFORMATTED T2 FLAIR CUBE
        T2SeriesRenameEnum.T2FLAIRCUBE_AXIr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXIr,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2FLAIRCUBE_SAGr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAGr,
            ContrastEnum.NE,
        },
        T2SeriesRenameEnum.T2FLAIRCUBE_CORr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.CORr,
            ContrastEnum.NE,
        },
        # REFORMATTED T2 FLAIR CUBE with Contrast
        T2SeriesRenameEnum.T2FLAIRCUBECE_AXIr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.AXIr,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2FLAIRCUBECE_SAGr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.SAGr,
            ContrastEnum.CE,
        },
        T2SeriesRenameEnum.T2FLAIRCUBECE_CORr: {
            T2SeriesRenameEnum.T2,
            SeriesEnum.FLAIR,
            SeriesEnum.CUBE,
            ImageOrientationEnum.CORr,
            ContrastEnum.CE,
        },
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        MRAcquisitionTypeEnum.TYPE_3D,
    )

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()
    contrast_processing_strategy = ContrastProcessingStrategy()

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
    def get_contrast(cls, dicom_ds: DicomDataset) -> Union[BaseEnum, ContrastEnum]:
        """獲取對比劑資訊"""
        return cls.contrast_processing_strategy.process(dicom_ds)

    @classmethod
    def get_series_type(
        cls, dicom_ds: DicomDataset
    ) -> Union[SeriesEnum, T2SeriesRenameEnum, NullEnum]:
        """獲取序列類型"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        desc = series_description.value.upper()

        if "FLAIR" in desc:
            return SeriesEnum.FLAIR
        elif "CUBE" in desc:
            return SeriesEnum.CUBE
        elif "T2" in desc:
            return T2SeriesRenameEnum.T2

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 T2 序列"""
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

            # 根據獲取類型處理
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
                f"T2 處理失敗: {str(e)}",
                processing_stage="t2_processing",
                details={"dicom_ds": str(dicom_ds)},
            ) from e

    def _process_type(
        self, dicom_ds: DicomDataset, series_mapping: dict, rename_dict: dict
    ) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理特定類型的 T2 序列 - 使用函數式 RORO 模式"""
        # 建立處理請求物件 (RORO 模式)
        processing_request = ProcessingRequest(
            dicom_dataset=dicom_ds,
            processing_options={"strategy_type": "T2"},
            series_context={"mapping_type": "type_specific"},
        )

        # 建立屬性提取器列表 (函數式組合)
        attribute_extractors = create_attribute_extractor_list(
            self.get_image_orientation, self.get_contrast, self.get_series_type
        )

        # 使用函數式處理 (RORO 模式)
        processing_result = process_series_with_type_mapping(
            processing_request, series_mapping, rename_dict, attribute_extractors
        )

        return processing_result.result_enum
