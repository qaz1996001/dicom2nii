"""
函數式程式設計輔助工具 - 遵循 .cursor 規則
"""

from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar, Union

from ..core.enums import BaseEnum, ImageOrientationEnum, NullEnum
from ..core.types import DicomDataset

T = TypeVar("T")
R = TypeVar("R")


@dataclass
class ProcessingRequest:
    """處理請求物件 - 實施 RORO 模式"""

    dicom_dataset: DicomDataset
    processing_options: dict[str, Any]
    series_context: dict[str, Any]


@dataclass
class ProcessingResult:
    """處理結果物件 - 實施 RORO 模式"""

    success: bool
    result_enum: Union[BaseEnum, Any]
    processing_stage: str
    details: dict[str, Any]
    errors: list[str]


def get_image_orientation_with_reformatted_check(
    dicom_ds: DicomDataset, orientation_strategy: Any
) -> Union[BaseEnum, ImageOrientationEnum]:
    """獲取包含 REFORMATTED 檢查的影像方向 - 純函數實作

    Args:
        dicom_ds: DICOM 資料集
        orientation_strategy: 影像方向處理策略

    Returns:
        影像方向枚舉 (可能包含 r 後綴)
    """
    # Early Return - 檢查必要資料
    image_orientation = orientation_strategy.process(dicom_ds=dicom_ds)
    image_type = dicom_ds.get((0x08, 0x08))

    if not image_type or len(image_type.value) < 3:
        return image_orientation

    # 檢查是否為重新格式化影像
    is_reformatted = image_type.value[2] == "REFORMATTED"

    if not is_reformatted:
        return image_orientation

    # 宣告式映射 - 重新格式化方向
    reformatted_orientation_map = {
        ImageOrientationEnum.AXI: ImageOrientationEnum.AXIr,
        ImageOrientationEnum.SAG: ImageOrientationEnum.SAGr,
        ImageOrientationEnum.COR: ImageOrientationEnum.CORr,
    }

    return reformatted_orientation_map.get(image_orientation, image_orientation)


def extract_series_attributes(dicom_ds: DicomDataset) -> dict[str, Any]:
    """提取序列屬性 - 純函數，遵循 RORO 模式

    Args:
        dicom_ds: DICOM 資料集

    Returns:
        序列屬性字典
    """
    series_description = dicom_ds.get((0x08, 0x103E))
    image_type = dicom_ds.get((0x08, 0x08))

    return {
        "has_series_description": series_description is not None,
        "series_description_value": series_description.value
        if series_description
        else "",
        "has_image_type": image_type is not None,
        "image_type_values": image_type.value if image_type else [],
        "is_reformatted": (
            image_type
            and len(image_type.value) > 2
            and image_type.value[2] == "REFORMATTED"
        ),
        "is_original_primary": (
            image_type
            and len(image_type.value) >= 2
            and "ORIGINAL" in image_type.value
            and "PRIMARY" in image_type.value
        ),
    }


def match_series_pattern(
    series_description: str, pattern_mapping: dict[Any, Any]
) -> Optional[Any]:
    """匹配序列模式 - 純函數

    Args:
        series_description: 序列描述
        pattern_mapping: 模式映射字典

    Returns:
        匹配的枚舉值或 None
    """
    if not series_description:
        return None

    for series_enum, pattern in pattern_mapping.items():
        if pattern.search(series_description):
            return series_enum

    return None


def find_matching_rename_enum(
    group_results: set, rename_dict: dict[Any, set]
) -> Optional[Any]:
    """尋找匹配的重新命名枚舉 - 純函數

    Args:
        group_results: 分組結果集合
        rename_dict: 重新命名字典

    Returns:
        匹配的重新命名枚舉或 None
    """
    for rename_enum, required_set in rename_dict.items():
        if required_set.issubset(group_results):
            return rename_enum

    return None


def process_series_with_type_mapping(
    processing_request: ProcessingRequest,
    series_mapping: dict[Any, Any],
    rename_dict: dict[Any, set],
    attribute_extractors: list[Callable[[DicomDataset], Any]],
) -> ProcessingResult:
    """使用類型映射處理序列 - RORO 模式實作

    Args:
        processing_request: 處理請求物件
        series_mapping: 序列映射
        rename_dict: 重新命名字典
        attribute_extractors: 屬性提取器函數列表

    Returns:
        處理結果物件
    """
    dicom_ds = processing_request.dicom_dataset
    series_attrs = extract_series_attributes(dicom_ds)

    # Early Return - 檢查序列描述
    if not series_attrs["has_series_description"]:
        return ProcessingResult(
            success=False,
            result_enum=NullEnum.NULL,
            processing_stage="series_description_check",
            details=series_attrs,
            errors=["序列描述缺失"],
        )

    # 匹配序列模式
    matched_series = match_series_pattern(
        series_attrs["series_description_value"], series_mapping
    )

    if not matched_series:
        return ProcessingResult(
            success=False,
            result_enum=NullEnum.NULL,
            processing_stage="pattern_matching",
            details=series_attrs,
            errors=["無匹配的序列模式"],
        )

    # 提取所有屬性
    group_results = {matched_series}

    for extractor in attribute_extractors:
        try:
            result = extractor(dicom_ds)
            if result != NullEnum.NULL:
                group_results.add(result)
        except Exception as e:
            return ProcessingResult(
                success=False,
                result_enum=NullEnum.NULL,
                processing_stage="attribute_extraction",
                details={"extractor": extractor.__name__, "error": str(e)},
                errors=[f"屬性提取失敗: {str(e)}"],
            )

    # 尋找匹配的重新命名
    rename_enum = find_matching_rename_enum(group_results, rename_dict)

    if rename_enum:
        return ProcessingResult(
            success=True,
            result_enum=rename_enum,
            processing_stage="completed",
            details={
                "matched_series": str(matched_series),
                "group_results": [str(r) for r in group_results],
                "series_attributes": series_attrs,
            },
            errors=[],
        )

    return ProcessingResult(
        success=False,
        result_enum=NullEnum.NULL,
        processing_stage="rename_matching",
        details={
            "matched_series": str(matched_series),
            "group_results": [str(r) for r in group_results],
        },
        errors=["無匹配的重新命名規則"],
    )


def create_attribute_extractor_list(
    image_orientation_fn: Callable, contrast_fn: Callable, series_type_fn: Callable
) -> list[Callable]:
    """建立屬性提取器列表 - 函數式組合

    Args:
        image_orientation_fn: 影像方向提取函數
        contrast_fn: 對比劑提取函數
        series_type_fn: 序列類型提取函數

    Returns:
        屬性提取器函數列表
    """
    return [image_orientation_fn, contrast_fn, series_type_fn]
