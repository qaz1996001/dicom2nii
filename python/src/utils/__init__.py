"""
工具函數模組
"""

from .dicom_utils import (
    clean_dicom_dataset,
    extract_dicom_info,
    get_b_values,
    get_image_orientation_with_reformatted,
    parse_study_folder_name,
    validate_dicom_tags,
)
from .file_operations import (
    copy_directory_tree,
    create_directory,
    delete_file,
    find_files_by_pattern,
    get_directory_structure,
    get_file_size,
    move_file,
    safe_file_operation,
)
from .functional_helpers import (
    ProcessingRequest,
    ProcessingResult,
    create_attribute_extractor_list,
    extract_series_attributes,
    find_matching_rename_enum,
    get_image_orientation_with_reformatted_check,
    match_series_pattern,
    process_series_with_type_mapping,
)
from .reporting import (
    create_processing_summary,
    generate_nifti_report,
    generate_series_report,
    generate_study_report,
)
from .validation import (
    validate_age_format,
    validate_conversion_params,
    validate_date_format,
    validate_dicom_file,
    validate_dicom_processing_params,
    validate_file_extension,
    validate_nifti_file,
    validate_path_exists,
    validate_study_folder_structure,
    validate_time_format,
    validate_upload_config,
)

__all__ = [
    # 檔案操作工具
    'create_directory',
    'safe_file_operation',
    'get_file_size',
    'copy_directory_tree',
    'move_file',
    'delete_file',
    'find_files_by_pattern',
    'get_directory_structure',

    # DICOM 工具
    'extract_dicom_info',
    'validate_dicom_tags',
    'get_b_values',
    'get_image_orientation_with_reformatted',
    'clean_dicom_dataset',
    'parse_study_folder_name',

    # 報告工具
    'generate_study_report',
    'generate_series_report',
    'generate_nifti_report',
    'create_processing_summary',

    # 驗證工具
    'validate_age_format',
    'validate_time_format',
    'validate_date_format',
    'validate_path_exists',
    'validate_file_extension',
    'validate_dicom_file',
    'validate_nifti_file',
    'validate_dicom_processing_params',
    'validate_conversion_params',
    'validate_upload_config',
    'validate_study_folder_structure',

    # 函數式程式設計輔助工具
    'ProcessingRequest',
    'ProcessingResult',
    'get_image_orientation_with_reformatted_check',
    'extract_series_attributes',
    'match_series_pattern',
    'find_matching_rename_enum',
    'process_series_with_type_mapping',
    'create_attribute_extractor_list',
]
