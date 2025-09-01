"""
自定義例外類別 - 遵循錯誤處理規則
"""

import traceback
from typing import Any, Optional


class Dicom2NiiError(Exception):
    """DICOM2NII 專案的基礎例外類別 - 遵循 Fail Fast 原則"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None, cause: Optional[Exception] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.cause = cause
        self.traceback_str = traceback.format_exc() if cause else None

    def to_dict(self) -> dict[str, Any]:
        """轉換為字典格式，便於日誌記錄"""
        return {
            "error_type": type(self).__name__,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None,
            "traceback": self.traceback_str
        }


class ProcessingError(Dicom2NiiError):
    """處理過程中發生的錯誤"""

    def __init__(self, message: str, processing_stage: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if processing_stage:
            details['processing_stage'] = processing_stage
        super().__init__(message, details, kwargs.get('cause'))


class ConversionError(Dicom2NiiError):
    """轉換過程中發生的錯誤"""

    def __init__(self, message: str, conversion_type: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if conversion_type:
            details['conversion_type'] = conversion_type
        super().__init__(message, details, kwargs.get('cause'))


class ConfigurationError(Dicom2NiiError):
    """配置相關的錯誤 - 提供使用者友好的錯誤訊息"""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        super().__init__(message, details, kwargs.get('cause'))


class FileOperationError(Dicom2NiiError):
    """檔案操作相關的錯誤"""

    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if file_path:
            details['file_path'] = file_path
        if operation:
            details['operation'] = operation
        super().__init__(message, details, kwargs.get('cause'))


class UploadError(Dicom2NiiError):
    """上傳過程中發生的錯誤"""

    def __init__(self, message: str, upload_target: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if upload_target:
            details['upload_target'] = upload_target
        super().__init__(message, details, kwargs.get('cause'))


class ValidationError(Dicom2NiiError):
    """驗證失敗的錯誤 - 提供具體的驗證失敗原因"""

    def __init__(self, message: str, field_name: Optional[str] = None, field_value: Optional[Any] = None, **kwargs):
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if field_value is not None:
            details['field_value'] = str(field_value)
        super().__init__(message, details, kwargs.get('cause'))


class DicomParsingError(ProcessingError):
    """DICOM 檔案解析錯誤"""

    def __init__(self, message: str, dicom_file: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if dicom_file:
            details['dicom_file'] = dicom_file
        super().__init__(message, processing_stage="dicom_parsing", details=details, cause=kwargs.get('cause'))


class NiftiProcessingError(ProcessingError):
    """NIfTI 檔案處理錯誤"""

    def __init__(self, message: str, nifti_file: Optional[str] = None, **kwargs):
        details = kwargs.get('details', {})
        if nifti_file:
            details['nifti_file'] = nifti_file
        super().__init__(message, processing_stage="nifti_processing", details=details, cause=kwargs.get('cause'))


# 錯誤處理裝飾器 - 實施 Guard Clauses 模式
def handle_errors(operation_name: str, logger=None):
    """錯誤處理裝飾器 - 實施統一的錯誤處理模式

    Args:
        operation_name: 操作名稱
        logger: 日誌記錄器 (可選)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Dicom2NiiError:
                # 重新拋出已知的專案例外
                raise
            except Exception as e:
                # 包裝未知例外
                error = Dicom2NiiError(
                    f"{operation_name} 操作失敗: {str(e)}",
                    details={"function": func.__name__, "args": str(args), "kwargs": str(kwargs)},
                    cause=e
                )

                if logger:
                    logger.log_error(error)

                raise error
        return wrapper
    return decorator


def validate_required_params(**params) -> None:
    """驗證必要參數 - 實施 Early Return 模式

    Args:
        **params: 參數字典，key 為參數名稱，value 為參數值

    Raises:
        ValidationError: 當必要參數缺失時
    """
    for param_name, param_value in params.items():
        if param_value is None:
            raise ValidationError(
                f"必要參數 '{param_name}' 不能為 None",
                field_name=param_name,
                field_value=param_value
            )

        if isinstance(param_value, str) and not param_value.strip():
            raise ValidationError(
                f"必要參數 '{param_name}' 不能為空字串",
                field_name=param_name,
                field_value=param_value
            )
