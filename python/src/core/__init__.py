"""
核心模組 - 提供基礎的類別、配置和型別定義
"""

from .config import Config
from .enums import (
    ASLSEQSeriesRenameEnum,
    BaseEnum,
    BodyPartEnum,
    ContrastEnum,
    CTSeriesRenameEnum,
    DSCSeriesRenameEnum,
    DTISeriesEnum,
    EchoTimeEnum,
    ImageOrientationEnum,
    ModalityEnum,
    MRAcquisitionTypeEnum,
    MRSeriesRenameEnum,
    NullEnum,
    RepetitionTimeEnum,
    SeriesEnum,
    T1SeriesRenameEnum,
    T2SeriesRenameEnum,
)
from .exceptions import (
    ConfigurationError,
    ConversionError,
    Dicom2NiiError,
    DicomParsingError,
    FileOperationError,
    NiftiProcessingError,
    ProcessingError,
    UploadError,
    ValidationError,
    handle_errors,
    validate_required_params,
)
from .logging import StructuredLogger, get_logger, setup_logging
from .types import (
    ConfigDict,
    Converter,
    DicomDataset,
    DicomTag,
    ExecutorType,
    Manager,
    PathLike,
    ProcessingResult,
    ProcessingStrategy,
    StrategyList,
)

__all__ = [
    "Config",
    # 枚舉類別
    "BaseEnum",
    "NullEnum",
    "ModalityEnum",
    "MRAcquisitionTypeEnum",
    "ImageOrientationEnum",
    "ContrastEnum",
    "RepetitionTimeEnum",
    "EchoTimeEnum",
    "BodyPartEnum",
    "SeriesEnum",
    "CTSeriesRenameEnum",
    "MRSeriesRenameEnum",
    "T1SeriesRenameEnum",
    "T2SeriesRenameEnum",
    "ASLSEQSeriesRenameEnum",
    "DSCSeriesRenameEnum",
    "DTISeriesEnum",
    # 例外類別
    "Dicom2NiiError",
    "ProcessingError",
    "ConversionError",
    "ConfigurationError",
    "FileOperationError",
    "UploadError",
    "ValidationError",
    "DicomParsingError",
    "NiftiProcessingError",
    "handle_errors",
    "validate_required_params",
    # 型別
    "PathLike",
    "ProcessingResult",
    "StrategyList",
    "ExecutorType",
    "ProcessingStrategy",
    "Manager",
    "Converter",
    "DicomDataset",
    "DicomTag",
    "ConfigDict",
    # 日誌記錄
    "StructuredLogger",
    "get_logger",
    "setup_logging",
]
