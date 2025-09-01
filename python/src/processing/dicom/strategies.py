"""
DICOM 處理策略實作
"""

import re
from typing import Union

try:
    from pydicom import FileDataset
except ImportError:
    # 如果 pydicom 未安裝，定義空的類別
    class FileDataset:
        pass

from ...core.enums import (
    ASLSEQSeriesRenameEnum,
    BaseEnum,
    ContrastEnum,
    DSCSeriesRenameEnum,
    ImageOrientationEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
    SeriesEnum,
    T1SeriesRenameEnum,
    T2SeriesRenameEnum,
)
from ...core.exceptions import ProcessingError
from ...core.types import DicomDataset
from ...utils.dicom_utils import get_b_values
from ..base import (
    ContrastProcessingStrategy,
    ImageOrientationProcessingStrategy,
    MRRenameSeriesProcessingStrategy,
)


class DwiProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """DWI 處理策略"""

    # 2D 序列重新命名映射
    type_2d_series_rename_mapping = {
        MRSeriesRenameEnum.DWI: re.compile('.*(DWI|AUTODIFF).*', re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (MRAcquisitionTypeEnum.TYPE_2D,)

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
            ImageOrientationEnum.AXI
        },
    }

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()
    series_group_fn_list: list = []

    @classmethod
    def get_series_group_fn_list(cls) -> list:
        """獲取序列分組函數列表"""
        if not cls.series_group_fn_list:
            cls.series_group_fn_list.extend([
                cls.get_image_orientation,
                cls.get_b_values
            ])
        return cls.series_group_fn_list

    @classmethod
    def get_image_orientation(cls, dicom_ds: DicomDataset) -> Union[BaseEnum, ImageOrientationEnum]:
        """獲取影像方向資訊，包含 REFORMATTED 檢查 - 遵循 .cursor 規則"""
        # Early Return 模式 - 檢查必要標籤
        image_orientation = cls.image_orientation_processing_strategy.process(dicom_ds=dicom_ds)
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type or len(image_type.value) < 3:
            return image_orientation

        # 檢查是否為 REFORMATTED 影像
        is_reformatted = image_type.value[2] == 'REFORMATTED'

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
    def get_b_values(cls, dicom_ds: DicomDataset) -> Union[MRSeriesRenameEnum, NullEnum]:
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
            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 根據獲取類型處理
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_2d_type(dicom_ds)

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"DWI 處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})

    def _process_2d_type(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
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
                for rename_enum, required_set in self.type_2d_series_rename_dict.items():
                    if required_set.issubset(group_results):
                        return rename_enum

        return NullEnum.NULL


class ADCProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """ADC 處理策略"""

    type_2d_series_rename_mapping = {
        MRSeriesRenameEnum.ADC: re.compile('.*(ADC).*', re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (MRAcquisitionTypeEnum.TYPE_2D,)

    type_2d_series_rename_dict = {
        MRSeriesRenameEnum.ADC: {
            MRSeriesRenameEnum.ADC,
            ImageOrientationEnum.AXI,
        },
    }

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()

    @classmethod
    def get_image_orientation(cls, dicom_ds: DicomDataset) -> Union[BaseEnum, ImageOrientationEnum]:
        """獲取影像方向資訊，包含 REFORMATTED 檢查 - 遵循 .cursor 規則"""
        # Early Return 模式 - 檢查必要標籤
        image_orientation = cls.image_orientation_processing_strategy.process(dicom_ds=dicom_ds)
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type or len(image_type.value) < 3:
            return image_orientation

        # 檢查是否為 REFORMATTED 影像
        is_reformatted = image_type.value[2] == 'REFORMATTED'

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
            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
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
                    for rename_enum, required_set in self.type_2d_series_rename_dict.items():
                        if {series_enum, image_orientation}.issubset(required_set):
                            return rename_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"ADC 處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})


class SWANProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """SWAN 處理策略"""

    type_2d_series_rename_mapping = {
        MRSeriesRenameEnum.SWAN: re.compile('.*(SWAN).*', re.IGNORECASE),
    }

    type_3d_series_rename_mapping = {
        MRSeriesRenameEnum.SWAN: re.compile('.*(SWAN).*', re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        MRAcquisitionTypeEnum.TYPE_3D
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
    def get_image_orientation(cls, dicom_ds: DicomDataset) -> Union[BaseEnum, ImageOrientationEnum]:
        """獲取影像方向資訊，包含 REFORMATTED 檢查 - 遵循 .cursor 規則"""
        # Early Return 模式 - 檢查必要標籤
        image_orientation = cls.image_orientation_processing_strategy.process(dicom_ds=dicom_ds)
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type or len(image_type.value) < 3:
            return image_orientation

        # 檢查是否為 REFORMATTED 影像
        is_reformatted = image_type.value[2] == 'REFORMATTED'

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
                if 'ORIGINAL' in image_type_values and 'PRIMARY' in image_type_values:
                    return SeriesEnum.ORIGINAL
                elif 'DERIVED' in image_type_values:
                    series_description = dicom_ds.get((0x08, 0x103E))
                    if series_description:
                        desc = series_description.value.upper()
                        if 'MIP' in desc:
                            return SeriesEnum.mIP
                        elif 'PHASE' in desc:
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
            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 根據獲取類型選擇處理方式
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_type(dicom_ds, self.type_2d_series_rename_mapping, self.type_2d_series_rename_dict)
            elif mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_3D:
                return self._process_type(dicom_ds, self.type_3d_series_rename_mapping, self.type_3d_series_rename_dict)

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"SWAN 處理失敗: {str(e)}", details={'dicom_ds': dicom_ds})

    def _process_type(self, dicom_ds: DicomDataset,
                     series_mapping: dict,
                     rename_dict: dict) -> Union[BaseEnum, MRSeriesRenameEnum]:
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


class EADCProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """Enhanced ADC 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.eADC: re.compile('.*(eADC).*', re.IGNORECASE),
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum, NullEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_3D,
        NullEnum.NULL
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
            raise ProcessingError(f"eADC 處理失敗: {str(e)}", processing_stage="eadc_processing")


class ESWANProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """Enhanced SWAN 處理策略 - 遵循 .cursor 規則"""

    series_rename_mapping = {
        MRSeriesRenameEnum.eSWAN: re.compile('.*(SWAN).*', re.IGNORECASE),
    }

    series_rename_dict = {
        MRSeriesRenameEnum.eSWAN: {SeriesEnum.eSWAN, SeriesEnum.ORIGINAL},
        MRSeriesRenameEnum.eSWANmIP: {SeriesEnum.eSWAN, SeriesEnum.mIP},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (MRAcquisitionTypeEnum.TYPE_3D,)

    @classmethod
    def get_mip_info(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, NullEnum]:
        """獲取 mIP 資訊 - 純函數實作"""
        image_type = dicom_ds.get((0x08, 0x08))
        instance_creation_time = dicom_ds.get((0x08, 0x13))

        if not image_type or not instance_creation_time:
            return NullEnum.NULL

        # 檢查是否為 MIN IP 或 REFORMATTED
        is_min_ip = (
            len(image_type.value) > 0 and
            image_type.value[-1] in ['MIN IP', 'REFORMATTED']
        )

        return SeriesEnum.mIP if is_min_ip else NullEnum.NULL

    @classmethod
    def get_original_info(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, NullEnum]:
        """獲取 ORIGINAL 資訊 - 純函數實作"""
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type:
            return NullEnum.NULL

        # 檢查是否為 ORIGINAL
        is_original = 'ORIGINAL' in image_type.value

        return SeriesEnum.ORIGINAL if is_original else NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 Enhanced SWAN 序列"""
        try:
            # Guard Clauses
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            series_description = dicom_ds.get((0x08, 0x103E))
            if not series_description:
                return NullEnum.NULL

            # 檢查序列描述匹配
            for _series_enum, pattern in self.series_rename_mapping.items():
                if pattern.match(series_description.value):
                    # 獲取序列分組資訊
                    group_results = {
                        SeriesEnum.eSWAN,
                        self.get_mip_info(dicom_ds),
                        self.get_original_info(dicom_ds),
                    }

                    # 移除 NULL 值
                    group_results.discard(NullEnum.NULL)

                    # 匹配重新命名字典
                    for rename_enum, required_set in self.series_rename_dict.items():
                        if required_set.issubset(group_results):
                            return rename_enum

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"eSWAN 處理失敗: {str(e)}", processing_stage="eswan_processing")


class T1ProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """T1 處理策略 - 完整實作"""

    # 序列重新命名映射
    series_rename_mapping = {
        T1SeriesRenameEnum.T1: re.compile('.*(T1|AX|COR|SAG).*', re.IGNORECASE),
        SeriesEnum.FLAIR: re.compile('(FLAIR)', re.IGNORECASE),
        SeriesEnum.CUBE: re.compile('.*(CUBE).*', re.IGNORECASE),
        SeriesEnum.BRAVO: re.compile('.*(BRAVO|FSPGR).*', re.IGNORECASE),
    }

    type_3d_series_rename_mapping = series_rename_mapping
    type_2d_series_rename_mapping = {
        T1SeriesRenameEnum.T1: re.compile('.*(T1).*', re.IGNORECASE),
        SeriesEnum.FLAIR: re.compile('(FLAIR)', re.IGNORECASE),
    }

    # 2D 序列重新命名字典
    type_2d_series_rename_dict = {
        T1SeriesRenameEnum.T1_AXI: {T1SeriesRenameEnum.T1, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T1SeriesRenameEnum.T1_SAG: {T1SeriesRenameEnum.T1, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T1SeriesRenameEnum.T1_COR: {T1SeriesRenameEnum.T1, ImageOrientationEnum.COR, ContrastEnum.NE},
        T1SeriesRenameEnum.T1CE_AXI: {T1SeriesRenameEnum.T1, ImageOrientationEnum.AXI, ContrastEnum.CE},
        T1SeriesRenameEnum.T1CE_SAG: {T1SeriesRenameEnum.T1, ImageOrientationEnum.SAG, ContrastEnum.CE},
        T1SeriesRenameEnum.T1CE_COR: {T1SeriesRenameEnum.T1, ImageOrientationEnum.COR, ContrastEnum.CE},
        T1SeriesRenameEnum.T1FLAIR_AXI: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIR_SAG: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIR_COR: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, ImageOrientationEnum.COR, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIRCE_AXI: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, ImageOrientationEnum.AXI, ContrastEnum.CE},
        T1SeriesRenameEnum.T1FLAIRCE_SAG: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, ImageOrientationEnum.SAG, ContrastEnum.CE},
        T1SeriesRenameEnum.T1FLAIRCE_COR: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, ImageOrientationEnum.COR, ContrastEnum.CE},
    }

    # 3D 序列重新命名字典 (完整版，包含 REFORMATTED)
    type_3d_series_rename_dict = {
        # ORIGINAL/PRIMARY T1 CUBE
        T1SeriesRenameEnum.T1CUBE_AXI: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T1SeriesRenameEnum.T1CUBE_SAG: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T1SeriesRenameEnum.T1CUBE_COR: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.COR, ContrastEnum.NE},

        # REFORMATTED T1 CUBE
        T1SeriesRenameEnum.T1CUBE_AXIr: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.NE},
        T1SeriesRenameEnum.T1CUBE_SAGr: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.NE},
        T1SeriesRenameEnum.T1CUBE_CORr: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.NE},

        # ORIGINAL/PRIMARY T1 CUBE with Contrast
        T1SeriesRenameEnum.T1CUBECE_AXI: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.AXI, ContrastEnum.CE},
        T1SeriesRenameEnum.T1CUBECE_SAG: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.SAG, ContrastEnum.CE},
        T1SeriesRenameEnum.T1CUBECE_COR: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.COR, ContrastEnum.CE},

        # REFORMATTED T1 CUBE with Contrast
        T1SeriesRenameEnum.T1CUBECE_AXIr: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.CE},
        T1SeriesRenameEnum.T1CUBECE_SAGr: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.CE},
        T1SeriesRenameEnum.T1CUBECE_CORr: {T1SeriesRenameEnum.T1, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.CE},

        # ORIGINAL/PRIMARY T1 FLAIR CUBE
        T1SeriesRenameEnum.T1FLAIRCUBE_AXI: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIRCUBE_SAG: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIRCUBE_COR: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.COR, ContrastEnum.NE},

        # REFORMATTED T1 FLAIR CUBE
        T1SeriesRenameEnum.T1FLAIRCUBE_AXIr: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIRCUBE_SAGr: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.NE},
        T1SeriesRenameEnum.T1FLAIRCUBE_CORr: {T1SeriesRenameEnum.T1, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.NE},

        # ORIGINAL/PRIMARY T1 BRAVO
        T1SeriesRenameEnum.T1BRAVO_AXI: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T1SeriesRenameEnum.T1BRAVO_SAG: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T1SeriesRenameEnum.T1BRAVO_COR: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.COR, ContrastEnum.NE},

        # REFORMATTED T1 BRAVO
        T1SeriesRenameEnum.T1BRAVO_AXIr: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.AXIr, ContrastEnum.NE},
        T1SeriesRenameEnum.T1BRAVO_SAGr: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.SAGr, ContrastEnum.NE},
        T1SeriesRenameEnum.T1BRAVO_CORr: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.CORr, ContrastEnum.NE},

        # REFORMATTED T1 BRAVO with Contrast
        T1SeriesRenameEnum.T1BRAVOCE_AXIr: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.AXIr, ContrastEnum.CE},
        T1SeriesRenameEnum.T1BRAVOCE_SAGr: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.SAGr, ContrastEnum.CE},
        T1SeriesRenameEnum.T1BRAVOCE_CORr: {T1SeriesRenameEnum.T1, SeriesEnum.BRAVO, ImageOrientationEnum.CORr, ContrastEnum.CE},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        MRAcquisitionTypeEnum.TYPE_3D
    )

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()
    contrast_processing_strategy = ContrastProcessingStrategy()

    @classmethod
    def get_image_orientation(cls, dicom_ds: DicomDataset) -> Union[BaseEnum, ImageOrientationEnum]:
        """獲取影像方向資訊，包含 REFORMATTED 檢查 - 遵循 .cursor 規則"""
        # Early Return 模式 - 檢查必要標籤
        image_orientation = cls.image_orientation_processing_strategy.process(dicom_ds=dicom_ds)
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type or len(image_type.value) < 3:
            return image_orientation

        # 檢查是否為 REFORMATTED 影像
        is_reformatted = image_type.value[2] == 'REFORMATTED'

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
    def get_series_type(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, T1SeriesRenameEnum, NullEnum]:
        """獲取序列類型"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        desc = series_description.value.upper()

        if 'FLAIR' in desc:
            return SeriesEnum.FLAIR
        elif 'CUBE' in desc:
            return SeriesEnum.CUBE
        elif 'BRAVO' in desc or 'FSPGR' in desc:
            return SeriesEnum.BRAVO
        elif 'T1' in desc:
            return T1SeriesRenameEnum.T1

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 T1 序列"""
        try:
            # Guard Clauses - Early Return 模式
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 根據獲取類型處理
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_type(dicom_ds, self.type_2d_series_rename_mapping, self.type_2d_series_rename_dict)
            elif mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_3D:
                return self._process_type(dicom_ds, self.type_3d_series_rename_mapping, self.type_3d_series_rename_dict)

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"T1 處理失敗: {str(e)}", processing_stage="t1_processing", details={'dicom_ds': str(dicom_ds)})

    def _process_type(self, dicom_ds: DicomDataset, series_mapping: dict, rename_dict: dict) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理特定類型的 T1 序列 - 使用函數式 RORO 模式"""
        from ...utils.functional_helpers import (
            ProcessingRequest,
            create_attribute_extractor_list,
            process_series_with_type_mapping,
        )

        # 建立處理請求物件 (RORO 模式)
        processing_request = ProcessingRequest(
            dicom_dataset=dicom_ds,
            processing_options={'strategy_type': 'T1'},
            series_context={'mapping_type': 'type_specific'}
        )

        # 建立屬性提取器列表 (函數式組合)
        attribute_extractors = create_attribute_extractor_list(
            self.get_image_orientation,
            self.get_contrast,
            self.get_series_type
        )

        # 使用函數式處理 (RORO 模式)
        processing_result = process_series_with_type_mapping(
            processing_request,
            series_mapping,
            rename_dict,
            attribute_extractors
        )

        return processing_result.result_enum


class T2ProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """T2 處理策略 - 完整實作"""

    # 序列重新命名映射
    series_rename_mapping = {
        T2SeriesRenameEnum.T2: re.compile('.*(T2).*', re.IGNORECASE),
        SeriesEnum.FLAIR: re.compile('(FLAIR)', re.IGNORECASE),
        SeriesEnum.CUBE: re.compile('.*(CUBE).*', re.IGNORECASE),
    }

    type_3d_series_rename_mapping = series_rename_mapping
    type_2d_series_rename_mapping = {
        T2SeriesRenameEnum.T2: re.compile('.*(T2).*', re.IGNORECASE),
        SeriesEnum.FLAIR: re.compile('(FLAIR)', re.IGNORECASE),
    }

    # 2D 序列重新命名字典
    type_2d_series_rename_dict = {
        T2SeriesRenameEnum.T2_AXI: {T2SeriesRenameEnum.T2, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T2SeriesRenameEnum.T2_SAG: {T2SeriesRenameEnum.T2, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T2SeriesRenameEnum.T2_COR: {T2SeriesRenameEnum.T2, ImageOrientationEnum.COR, ContrastEnum.NE},
        T2SeriesRenameEnum.T2CE_AXI: {T2SeriesRenameEnum.T2, ImageOrientationEnum.AXI, ContrastEnum.CE},
        T2SeriesRenameEnum.T2CE_SAG: {T2SeriesRenameEnum.T2, ImageOrientationEnum.SAG, ContrastEnum.CE},
        T2SeriesRenameEnum.T2CE_COR: {T2SeriesRenameEnum.T2, ImageOrientationEnum.COR, ContrastEnum.CE},
        T2SeriesRenameEnum.T2FLAIR_AXI: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T2SeriesRenameEnum.T2FLAIR_SAG: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T2SeriesRenameEnum.T2FLAIR_COR: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, ImageOrientationEnum.COR, ContrastEnum.NE},
    }

    # 3D 序列重新命名字典 (完整版，包含 REFORMATTED)
    type_3d_series_rename_dict = {
        # ORIGINAL/PRIMARY T2 CUBE
        T2SeriesRenameEnum.T2CUBE_AXI: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T2SeriesRenameEnum.T2CUBE_SAG: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T2SeriesRenameEnum.T2CUBE_COR: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.COR, ContrastEnum.NE},

        # REFORMATTED T2 CUBE
        T2SeriesRenameEnum.T2CUBE_AXIr: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.NE},
        T2SeriesRenameEnum.T2CUBE_SAGr: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.NE},
        T2SeriesRenameEnum.T2CUBE_CORr: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.NE},

        # ORIGINAL/PRIMARY T2 CUBE with Contrast
        T2SeriesRenameEnum.T2CUBECE_AXI: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.AXI, ContrastEnum.CE},
        T2SeriesRenameEnum.T2CUBECE_SAG: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.SAG, ContrastEnum.CE},
        T2SeriesRenameEnum.T2CUBECE_COR: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.COR, ContrastEnum.CE},

        # REFORMATTED T2 CUBE with Contrast
        T2SeriesRenameEnum.T2CUBECE_AXIr: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.CE},
        T2SeriesRenameEnum.T2CUBECE_SAGr: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.CE},
        T2SeriesRenameEnum.T2CUBECE_CORr: {T2SeriesRenameEnum.T2, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.CE},

        # ORIGINAL/PRIMARY T2 FLAIR CUBE
        T2SeriesRenameEnum.T2FLAIRCUBE_AXI: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.AXI, ContrastEnum.NE},
        T2SeriesRenameEnum.T2FLAIRCUBE_SAG: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.SAG, ContrastEnum.NE},
        T2SeriesRenameEnum.T2FLAIRCUBE_COR: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.COR, ContrastEnum.NE},

        # REFORMATTED T2 FLAIR CUBE
        T2SeriesRenameEnum.T2FLAIRCUBE_AXIr: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.NE},
        T2SeriesRenameEnum.T2FLAIRCUBE_SAGr: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.NE},
        T2SeriesRenameEnum.T2FLAIRCUBE_CORr: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.NE},

        # REFORMATTED T2 FLAIR CUBE with Contrast
        T2SeriesRenameEnum.T2FLAIRCUBECE_AXIr: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.AXIr, ContrastEnum.CE},
        T2SeriesRenameEnum.T2FLAIRCUBECE_SAGr: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.SAGr, ContrastEnum.CE},
        T2SeriesRenameEnum.T2FLAIRCUBECE_CORr: {T2SeriesRenameEnum.T2, SeriesEnum.FLAIR, SeriesEnum.CUBE, ImageOrientationEnum.CORr, ContrastEnum.CE},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        MRAcquisitionTypeEnum.TYPE_3D
    )

    image_orientation_processing_strategy = ImageOrientationProcessingStrategy()
    contrast_processing_strategy = ContrastProcessingStrategy()

    @classmethod
    def get_image_orientation(cls, dicom_ds: DicomDataset) -> Union[BaseEnum, ImageOrientationEnum]:
        """獲取影像方向資訊，包含 REFORMATTED 檢查 - 遵循 .cursor 規則"""
        # Early Return 模式 - 檢查必要標籤
        image_orientation = cls.image_orientation_processing_strategy.process(dicom_ds=dicom_ds)
        image_type = dicom_ds.get((0x08, 0x08))

        if not image_type or len(image_type.value) < 3:
            return image_orientation

        # 檢查是否為 REFORMATTED 影像
        is_reformatted = image_type.value[2] == 'REFORMATTED'

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
    def get_series_type(cls, dicom_ds: DicomDataset) -> Union[SeriesEnum, T2SeriesRenameEnum, NullEnum]:
        """獲取序列類型"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        desc = series_description.value.upper()

        if 'FLAIR' in desc:
            return SeriesEnum.FLAIR
        elif 'CUBE' in desc:
            return SeriesEnum.CUBE
        elif 'T2' in desc:
            return T2SeriesRenameEnum.T2

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 T2 序列"""
        try:
            # Guard Clauses - Early Return 模式
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 根據獲取類型處理
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_type(dicom_ds, self.type_2d_series_rename_mapping, self.type_2d_series_rename_dict)
            elif mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_3D:
                return self._process_type(dicom_ds, self.type_3d_series_rename_mapping, self.type_3d_series_rename_dict)

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"T2 處理失敗: {str(e)}", processing_stage="t2_processing", details={'dicom_ds': str(dicom_ds)})

    def _process_type(self, dicom_ds: DicomDataset, series_mapping: dict, rename_dict: dict) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理特定類型的 T2 序列 - 使用函數式 RORO 模式"""
        from ...utils.functional_helpers import (
            ProcessingRequest,
            create_attribute_extractor_list,
            process_series_with_type_mapping,
        )

        # 建立處理請求物件 (RORO 模式)
        processing_request = ProcessingRequest(
            dicom_dataset=dicom_ds,
            processing_options={'strategy_type': 'T2'},
            series_context={'mapping_type': 'type_specific'}
        )

        # 建立屬性提取器列表 (函數式組合)
        attribute_extractors = create_attribute_extractor_list(
            self.get_image_orientation,
            self.get_contrast,
            self.get_series_type
        )

        # 使用函數式處理 (RORO 模式)
        processing_result = process_series_with_type_mapping(
            processing_request,
            series_mapping,
            rename_dict,
            attribute_extractors
        )

        return processing_result.result_enum


class ASLProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """ASL (Arterial Spin Labeling) 處理策略"""

    # 序列重新命名映射
    series_rename_mapping = {
        ASLSEQSeriesRenameEnum.ASLSEQ: re.compile('(multi-Delay ASL SEQ)', re.IGNORECASE),
        ASLSEQSeriesRenameEnum.ASLPROD: re.compile('(3D ASL [(]non-contrast[)])', re.IGNORECASE),
        ASLSEQSeriesRenameEnum.ASLSEQATT: re.compile('([(]Transit delay[)] multi-Delay ASL SEQ)', re.IGNORECASE),
        ASLSEQSeriesRenameEnum.ASLSEQATT_COLOR: re.compile('([(]Color Transit delay[)] multi-Delay ASL SEQ)', re.IGNORECASE),
        ASLSEQSeriesRenameEnum.ASLSEQCBF: re.compile('([(]Transit corrected CBF[)] multi-Delay ASL SEQ)', re.IGNORECASE),
        ASLSEQSeriesRenameEnum.ASLSEQCBF_COLOR: re.compile('([(]Color Transit corrected CBF[)] multi-Delay ASL SEQ)', re.IGNORECASE),
        ASLSEQSeriesRenameEnum.ASLSEQPW: re.compile('([(]per del, mean PW, REF[)] multi-Delay ASL SEQ)', re.IGNORECASE),
    }

    type_3d_series_rename_mapping = series_rename_mapping
    type_3d_series_rename_dict = {}  # 根據需要填充

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum], ...] = (MRAcquisitionTypeEnum.TYPE_3D,)

    @classmethod
    def get_asl_info(cls, dicom_ds: DicomDataset) -> Union[ASLSEQSeriesRenameEnum, NullEnum]:
        """獲取 ASL 資訊"""
        # 檢查 ASL 標籤
        pulse_sequence_name = dicom_ds.get((0x19, 0x109c))
        if pulse_sequence_name and str(pulse_sequence_name.value).lower() == ASLSEQSeriesRenameEnum.ASL.value.lower():
            return ASLSEQSeriesRenameEnum.ASL

        # 檢查 ASL 技術標籤
        asl_technique = dicom_ds.get((0x43, 0x10A4))
        if asl_technique and ASLSEQSeriesRenameEnum.ASL.value.lower() in str(asl_technique.value).lower():
            return ASLSEQSeriesRenameEnum.ASL

        return NullEnum.NULL

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 ASL 序列"""
        try:
            # Guard Clauses
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
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
            raise ProcessingError(f"ASL 處理失敗: {str(e)}", processing_stage="asl_processing", details={'dicom_ds': str(dicom_ds)})


class DSCProcessingStrategy(MRRenameSeriesProcessingStrategy):
    """DSC (Dynamic Susceptibility Contrast) 處理策略"""

    # 序列重新命名映射
    series_rename_mapping = {
        DSCSeriesRenameEnum.DSC: re.compile('.*(AUTOPWI|Perfusion).*', re.IGNORECASE),
        DSCSeriesRenameEnum.rCBF: re.compile('.*(CBF).*', re.IGNORECASE),
        DSCSeriesRenameEnum.rCBV: re.compile('.*(CBV).*', re.IGNORECASE),
        DSCSeriesRenameEnum.MTT: re.compile('.*(MTT).*', re.IGNORECASE),
    }

    type_2d_series_rename_mapping = {
        DSCSeriesRenameEnum.DSC: re.compile('.*(AUTOPWI|Perfusion).*', re.IGNORECASE),
    }

    type_null_series_rename_mapping = {
        DSCSeriesRenameEnum.rCBF: re.compile('.*(CBF).*', re.IGNORECASE),
        DSCSeriesRenameEnum.rCBV: re.compile('.*(CBV).*', re.IGNORECASE),
        DSCSeriesRenameEnum.MTT: re.compile('.*(MTT).*', re.IGNORECASE),
    }

    type_null_series_rename_dict = {
        DSCSeriesRenameEnum.rCBF: {DSCSeriesRenameEnum.rCBF},
        DSCSeriesRenameEnum.rCBV: {DSCSeriesRenameEnum.rCBV},
        DSCSeriesRenameEnum.MTT: {DSCSeriesRenameEnum.MTT},
    }

    mr_acquisition_type: tuple[Union[MRAcquisitionTypeEnum, NullEnum], ...] = (
        MRAcquisitionTypeEnum.TYPE_2D,
        NullEnum.NULL
    )

    def process(self, dicom_ds: DicomDataset) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理 DSC 序列"""
        try:
            # Guard Clauses
            modality_enum = self.modality_processing_strategy.process(dicom_ds=dicom_ds)
            if modality_enum != self.modality:
                return NullEnum.NULL

            mr_acquisition_type_enum = self.mr_acquisition_type_processing_strategy.process(dicom_ds=dicom_ds)
            if mr_acquisition_type_enum not in self.mr_acquisition_type:
                return NullEnum.NULL

            # 根據獲取類型處理
            if mr_acquisition_type_enum == MRAcquisitionTypeEnum.TYPE_2D:
                return self._process_type(dicom_ds, self.type_2d_series_rename_mapping, {})
            elif mr_acquisition_type_enum == NullEnum.NULL:
                return self._process_type(dicom_ds, self.type_null_series_rename_mapping, self.type_null_series_rename_dict)

            return NullEnum.NULL

        except Exception as e:
            raise ProcessingError(f"DSC 處理失敗: {str(e)}", processing_stage="dsc_processing", details={'dicom_ds': str(dicom_ds)})

    def _process_type(self, dicom_ds: DicomDataset, series_mapping: dict, rename_dict: dict) -> Union[BaseEnum, MRSeriesRenameEnum]:
        """處理特定類型的 DSC 序列"""
        series_description = dicom_ds.get((0x08, 0x103E))
        if not series_description:
            return NullEnum.NULL

        # 檢查序列描述是否匹配
        for series_enum, pattern in series_mapping.items():
            if pattern.search(series_description.value):
                # 如果沒有重新命名字典，直接返回匹配的枚舉
                if not rename_dict:
                    return series_enum

                # 否則檢查重新命名字典
                for rename_enum, required_set in rename_dict.items():
                    if {series_enum}.issubset(required_set):
                        return rename_enum

        return NullEnum.NULL
