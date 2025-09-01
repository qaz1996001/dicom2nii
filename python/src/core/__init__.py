"""
核心模組 - 提供基礎的類別、配置和型別定義
"""

from .config import Config
from .enums import (
    BaseEnum, NullEnum, ModalityEnum, MRAcquisitionTypeEnum,
    ImageOrientationEnum, ContrastEnum, RepetitionTimeEnum, EchoTimeEnum,
    BodyPartEnum, SeriesEnum, CTSeriesRenameEnum, MRSeriesRenameEnum,
    T1SeriesRenameEnum, T2SeriesRenameEnum, ASLSEQSeriesRenameEnum,
    DSCSeriesRenameEnum, DTISeriesEnum
)
from .exceptions import (
    Dicom2NiiError, ProcessingError, ConversionError, ConfigurationError,
    FileOperationError, UploadError, ValidationError, DicomParsingError, 
    NiftiProcessingError, handle_errors, validate_required_params
)
from .types import (
    PathLike, ProcessingResult, StrategyList, ExecutorType,
    ProcessingStrategy, Manager, Converter, DicomDataset, DicomTag, ConfigDict
)
from .logging import StructuredLogger, get_logger, setup_logging

__all__ = [
    'Config',
    # 枚舉類別
    'BaseEnum', 'NullEnum', 'ModalityEnum', 'MRAcquisitionTypeEnum',
    'ImageOrientationEnum', 'ContrastEnum', 'RepetitionTimeEnum', 'EchoTimeEnum',
    'BodyPartEnum', 'SeriesEnum', 'CTSeriesRenameEnum', 'MRSeriesRenameEnum',
    'T1SeriesRenameEnum', 'T2SeriesRenameEnum', 'ASLSEQSeriesRenameEnum',
    'DSCSeriesRenameEnum', 'DTISeriesEnum',
    # 例外類別
    'Dicom2NiiError', 'ProcessingError', 'ConversionError', 'ConfigurationError',
    'FileOperationError', 'UploadError', 'ValidationError', 'DicomParsingError', 'NiftiProcessingError',
    'handle_errors', 'validate_required_params',
    # 型別
    'PathLike', 'ProcessingResult', 'StrategyList', 'ExecutorType',
    'ProcessingStrategy', 'Manager', 'Converter', 'DicomDataset', 'DicomTag', 'ConfigDict',
    # 日誌記錄
    'StructuredLogger', 'get_logger', 'setup_logging',
]
