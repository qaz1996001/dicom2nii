"""
結構化日誌記錄模組 - 根據錯誤處理規則實作
"""

import logging
import sys
import traceback
from pathlib import Path
from typing import Any, Optional

from .exceptions import Dicom2NiiError


class StructuredLogger:
    """結構化日誌記錄器 - 遵循錯誤處理規則"""

    def __init__(self, name: str, level: int = logging.INFO):
        """初始化結構化日誌記錄器

        Args:
            name: 日誌記錄器名稱
            level: 日誌等級
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 避免重複添加處理器
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self) -> None:
        """設定日誌處理器"""
        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 檔案處理器 (如果需要)
        # file_handler = logging.FileHandler('dicom2nii.log')
        # file_handler.setFormatter(console_formatter)
        # self.logger.addHandler(file_handler)

    def log_error(self, error: Exception, context: Optional[dict[str, Any]] = None) -> None:
        """記錄錯誤 - 遵循錯誤處理規則的結構化日誌

        Args:
            error: 例外物件
            context: 額外的上下文資訊
        """
        self.logger.error(
            "Operation failed",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "traceback": traceback.format_exc(),
                "context": context or {},
                "is_dicom2nii_error": isinstance(error, Dicom2NiiError)
            }
        )

    def log_processing_start(self, operation: str, details: dict[str, Any]) -> None:
        """記錄處理開始"""
        self.logger.info(
            f"Starting {operation}",
            extra={
                "operation": operation,
                "details": details,
                "stage": "start"
            }
        )

    def log_processing_success(self, operation: str, details: dict[str, Any]) -> None:
        """記錄處理成功"""
        self.logger.info(
            f"Completed {operation}",
            extra={
                "operation": operation,
                "details": details,
                "stage": "success"
            }
        )

    def log_processing_progress(self, operation: str, progress: dict[str, Any]) -> None:
        """記錄處理進度"""
        self.logger.info(
            f"Progress {operation}",
            extra={
                "operation": operation,
                "progress": progress,
                "stage": "progress"
            }
        )

    def log_file_operation(self, operation: str, file_path: Path, success: bool, details: Optional[dict] = None) -> None:
        """記錄檔案操作"""
        level = logging.INFO if success else logging.ERROR
        message = f"File {operation} {'succeeded' if success else 'failed'}"

        self.logger.log(
            level,
            message,
            extra={
                "operation": operation,
                "file_path": str(file_path),
                "success": success,
                "details": details or {}
            }
        )

    def log_conversion_stats(self, stats: dict[str, Any]) -> None:
        """記錄轉換統計資訊"""
        self.logger.info(
            "Conversion statistics",
            extra={
                "statistics": stats,
                "stage": "completion"
            }
        )


# 全域日誌記錄器實例
main_logger = StructuredLogger("dicom2nii.main")
processing_logger = StructuredLogger("dicom2nii.processing")
conversion_logger = StructuredLogger("dicom2nii.conversion")
upload_logger = StructuredLogger("dicom2nii.upload")


def get_logger(name: str) -> StructuredLogger:
    """獲取指定名稱的日誌記錄器

    Args:
        name: 日誌記錄器名稱

    Returns:
        結構化日誌記錄器實例
    """
    return StructuredLogger(f"dicom2nii.{name}")


def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """設定全域日誌配置

    Args:
        level: 日誌等級
        log_file: 日誌檔案路徑 (可選)
    """
    # 設定根日誌記錄器
    root_logger = logging.getLogger("dicom2nii")
    root_logger.setLevel(level)

    # 避免重複設定
    if root_logger.handlers:
        return

    # 控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # 檔案處理器 (如果指定)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
