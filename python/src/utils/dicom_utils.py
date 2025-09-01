"""
DICOM 相關工具函數
"""

import re
from typing import Any, Optional

try:
    from pydicom import Dataset, FileDataset
except ImportError:
    # 如果 pydicom 未安裝，定義空的類別以避免匯入錯誤
    class FileDataset:
        pass

    class Dataset:
        pass


from ..core.exceptions import ValidationError
from ..core.types import DicomDataset


def extract_dicom_info(dicom_ds: DicomDataset) -> dict[str, Any]:
    """提取 DICOM 檔案的基本資訊"""
    try:
        # 病人資訊
        patient_id = dicom_ds.get((0x10, 0x20))
        gender = dicom_ds.get((0x10, 0x40))
        birth_date = dicom_ds.get((0x10, 0x30))

        # 檢查資訊
        study_date = dicom_ds.get((0x08, 0x20))
        study_time = dicom_ds.get((0x08, 0x30))
        study_description = dicom_ds.get((0x08, 0x1030))
        accession_number = dicom_ds.get((0x08, 0x50))

        # 序列資訊
        series_date = dicom_ds.get((0x08, 0x21))
        series_time = dicom_ds.get((0x08, 0x31))
        modality = dicom_ds.get((0x08, 0x60))

        # 處理時間格式
        study_time_value = (
            study_time.value.split(".")[0]
            if study_time and "." in study_time.value
            else study_time.value
            if study_time
            else None
        )
        series_time_value = (
            series_time.value.split(".")[0]
            if series_time and "." in series_time.value
            else series_time.value
            if series_time
            else None
        )

        return {
            "patient_id": patient_id.value if patient_id else None,
            "gender": gender.value if gender else None,
            "birth_date": birth_date.value if birth_date else None,
            "study_date": study_date.value if study_date else None,
            "study_time": study_time_value,
            "study_description": study_description.value if study_description else None,
            "accession_number": accession_number.value if accession_number else None,
            "series_date": series_date.value if series_date else None,
            "series_time": series_time_value,
            "modality": modality.value if modality else None,
        }
    except Exception as e:
        raise ValidationError(f"提取 DICOM 資訊失敗: {str(e)}")


def validate_dicom_tags(
    dicom_ds: DicomDataset, required_tags: list[tuple[int, int]]
) -> bool:
    """驗證 DICOM 檔案是否包含必要的標籤"""
    try:
        for tag in required_tags:
            if dicom_ds.get(tag) is None:
                return False
        return True
    except Exception:
        return False


def get_b_values(dicom_ds: DicomDataset) -> Optional[int]:
    """獲取 DWI 的 b 值"""
    try:
        dicom_tag = dicom_ds.get((0x43, 0x1039))
        if dicom_tag and len(dicom_tag) > 0:
            return int(dicom_tag[0])
        return None
    except (ValueError, IndexError, TypeError):
        return None


def get_image_orientation_with_reformatted(
    dicom_ds: DicomDataset, image_orientation_strategy
) -> Any:
    """獲取包含重新格式化資訊的影像方向"""
    try:
        # 獲取基本影像方向
        image_orientation = image_orientation_strategy.process(dicom_ds=dicom_ds)

        # 檢查是否為重新格式化的影像
        image_type = dicom_ds.get((0x08, 0x08))
        if (
            image_type
            and len(image_type.value) > 2
            and image_type.value[2] == "REFORMATTED"
        ):
            # 根據原始方向返回重新格式化的方向
            orientation_map = {"AXI": "AXIr", "SAG": "SAGr", "COR": "CORr"}
            if (
                hasattr(image_orientation, "value")
                and image_orientation.value in orientation_map
            ):
                # 這裡需要返回對應的重新格式化枚舉值
                from ..core.enums import ImageOrientationEnum

                return getattr(
                    ImageOrientationEnum, orientation_map[image_orientation.value]
                )

        return image_orientation

    except Exception:
        from ..core.enums import NullEnum

        return NullEnum.NULL


def clean_dicom_dataset(
    dicom_ds: DicomDataset, exclude_tags: dict[str, str]
) -> DicomDataset:
    """清理 DICOM 資料集，移除不需要的標籤"""
    try:
        cleaned_ds = dicom_ds.copy()

        for tag_hex, _description in exclude_tags.items():
            tag_int = (int(tag_hex[:4], 16), int(tag_hex[4:], 16))
            if tag_int in cleaned_ds:
                del cleaned_ds[tag_int]

        return cleaned_ds

    except Exception as e:
        raise ValidationError(f"清理 DICOM 資料集失敗: {str(e)}")


def parse_study_folder_name(folder_name: str) -> Optional[dict[str, str]]:
    """解析檢查資料夾名稱"""
    pattern = re.compile(r"^(\d{8})_(\d{8})_(MR|CT)_(.*)$", re.IGNORECASE)
    match = pattern.match(folder_name)

    if match:
        return {
            "patient_id": match.group(1),
            "study_date": match.group(2),
            "modality": match.group(3),
            "description": match.group(4),
        }
    return None
