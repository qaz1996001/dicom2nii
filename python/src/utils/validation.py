"""
驗證工具函數 - 遵循 Python 一般原則和錯誤處理規則
"""

import re
from pathlib import Path
from typing import Any

from ..core.exceptions import ValidationError, validate_required_params


def validate_age_format(age_string: str) -> tuple[bool, str]:
    """驗證和格式化年齡字串"""
    try:
        pattern = re.compile(r'^(\d{3})Y$')

        if pattern.match(age_string):
            return False, age_string  # 已經是正確格式

        # 嘗試提取數字部分
        if age_string.isnumeric():
            return True, f"{int(age_string):03d}Y"
        elif age_string.endswith('Y'):
            age_num = int(age_string.split('Y')[0])
            return True, f"{age_num:03d}Y"
        else:
            raise ValidationError(f"無效的年齡格式: {age_string}")

    except (ValueError, IndexError) as e:
        raise ValidationError(f"年齡格式驗證失敗: {str(e)}")


def validate_date_format(date_string: str) -> str:
    """驗證日期格式 (YYYYMMDD)"""
    pattern = re.compile(r'^(\d{8})$')

    if pattern.match(date_string):
        return date_string
    else:
        raise ValidationError(f"無效的日期格式: {date_string}，應為 YYYYMMDD")


def validate_time_format(time_string: str) -> tuple[bool, str]:
    """驗證和格式化時間字串"""
    try:
        pattern = re.compile(r'^(\d{6})$')

        # 移除毫秒部分
        clean_time = time_string.split('.')[0]

        if pattern.match(clean_time):
            return False, clean_time  # 已經是正確格式

        # 嘗試格式化為 6 位數
        if clean_time.isnumeric():
            return True, f'{int(clean_time):06d}'
        else:
            raise ValidationError(f"無效的時間格式: {time_string}")

    except (ValueError, IndexError) as e:
        raise ValidationError(f"時間格式驗證失敗: {str(e)}")


def validate_path_exists(path: str) -> bool:
    """驗證路徑是否存在"""
    from pathlib import Path
    return Path(path).exists()


def validate_file_extension(file_path: str, expected_extensions: list[str]) -> bool:
    """驗證檔案副檔名"""
    from pathlib import Path
    file_ext = Path(file_path).suffix.lower()
    return file_ext in [ext.lower() for ext in expected_extensions]


def validate_dicom_file(file_path: str) -> bool:
    """驗證是否為有效的 DICOM 檔案"""
    try:
        from pydicom import dcmread
        dcmread(file_path, stop_before_pixels=True)
        return True
    except Exception:
        return False


def validate_nifti_file(file_path: str) -> bool:
    """驗證是否為有效的 NIfTI 檔案"""
    try:
        import nibabel as nib
        nib.load(file_path)
        return True
    except Exception:
        return False


def validate_dicom_processing_params(input_path: str, output_path: str, worker_count: int) -> None:
    """驗證 DICOM 處理參數 - 實施 Early Return 模式

    Args:
        input_path: 輸入路徑
        output_path: 輸出路徑
        worker_count: 工作執行緒數量

    Raises:
        ValidationError: 當參數無效時
    """
    # Guard Clauses - Early Return 模式
    validate_required_params(
        input_path=input_path,
        output_path=output_path,
        worker_count=worker_count
    )

    # 驗證輸入路徑存在
    if not validate_path_exists(input_path):
        raise ValidationError(
            f"輸入路徑不存在: {input_path}",
            field_name="input_path",
            field_value=input_path
        )

    # 驗證工作執行緒數量
    if not isinstance(worker_count, int) or worker_count < 1:
        raise ValidationError(
            f"工作執行緒數量必須為正整數: {worker_count}",
            field_name="worker_count",
            field_value=worker_count
        )

    if worker_count > 16:  # 合理的上限
        raise ValidationError(
            f"工作執行緒數量過大，建議不超過 16: {worker_count}",
            field_name="worker_count",
            field_value=worker_count
        )


def validate_conversion_params(input_files: list[str], output_dir: str) -> dict[str, list[str]]:
    """驗證轉換參數並返回驗證結果

    Args:
        input_files: 輸入檔案列表
        output_dir: 輸出目錄

    Returns:
        驗證結果字典，包含有效和無效的檔案
    """
    # Guard Clauses
    validate_required_params(input_files=input_files, output_dir=output_dir)

    if not input_files:
        raise ValidationError("輸入檔案列表不能為空", field_name="input_files")

    valid_files = []
    invalid_files = []

    for file_path in input_files:
        if validate_path_exists(file_path):
            if validate_file_extension(file_path, ['.dcm', '.nii.gz']):
                valid_files.append(file_path)
            else:
                invalid_files.append(f"{file_path} (不支援的檔案格式)")
        else:
            invalid_files.append(f"{file_path} (檔案不存在)")

    return {
        'valid_files': valid_files,
        'invalid_files': invalid_files,
        'total_files': len(input_files),
        'valid_count': len(valid_files),
        'invalid_count': len(invalid_files)
    }


def validate_upload_config(web_url: str, file_paths: list[str]) -> None:
    """驗證上傳配置參數

    Args:
        web_url: Web API URL
        file_paths: 要上傳的檔案路徑列表

    Raises:
        ValidationError: 當配置無效時
    """
    # Guard Clauses
    validate_required_params(web_url=web_url, file_paths=file_paths)

    # 驗證 URL 格式
    url_pattern = re.compile(
        r'^https?://'  # http:// 或 https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # 域名
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP 地址
        r'(?::\d+)?'  # 可選的端口號
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not url_pattern.match(web_url):
        raise ValidationError(
            f"無效的 URL 格式: {web_url}",
            field_name="web_url",
            field_value=web_url
        )

    # 驗證檔案路徑
    if not file_paths:
        raise ValidationError("檔案路徑列表不能為空", field_name="file_paths")

    for file_path in file_paths:
        if not validate_path_exists(file_path):
            raise ValidationError(
                f"檔案不存在: {file_path}",
                field_name="file_path",
                field_value=file_path
            )


def validate_study_folder_structure(study_path: str) -> dict[str, Any]:
    """驗證檢查資料夾結構

    Args:
        study_path: 檢查資料夾路徑

    Returns:
        驗證結果字典
    """
    validate_required_params(study_path=study_path)

    study_path_obj = Path(study_path)

    if not study_path_obj.exists():
        raise ValidationError(
            f"檢查資料夾不存在: {study_path}",
            field_name="study_path",
            field_value=study_path
        )

    if not study_path_obj.is_dir():
        raise ValidationError(
            f"路徑不是目錄: {study_path}",
            field_name="study_path",
            field_value=study_path
        )

    # 檢查資料夾結構
    series_folders = [item for item in study_path_obj.iterdir() if item.is_dir() and item.name != '.meta']
    meta_folder = study_path_obj / '.meta'
    dicom_files = list(study_path_obj.rglob('*.dcm'))
    nifti_files = list(study_path_obj.rglob('*.nii.gz'))

    return {
        'is_valid': True,
        'series_count': len(series_folders),
        'has_meta_folder': meta_folder.exists(),
        'dicom_file_count': len(dicom_files),
        'nifti_file_count': len(nifti_files),
        'series_folders': [f.name for f in series_folders]
    }
