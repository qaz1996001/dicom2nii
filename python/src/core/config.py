"""
統一配置管理
"""

import os
from pathlib import Path
from typing import Any, Optional


class Config:
    """統一配置管理類別"""

    # SQL 相關配置
    SQL_WEB_URL: str = os.getenv('SQL_WEB_URL', 'http://127.0.0.1:8800/api/')

    # 物件儲存相關配置
    OBJECT_WEB_URL: str = os.getenv('OBJECT_WEB_URL', 'http://127.0.0.1:9000')
    OBJECT_WEB_ACCESS_KEY: str = os.getenv('OBJECT_WEB_ACCESS_KEY', 'bHRhU4yBlvx1VkEVhdIC')
    OBJECT_WEB_SECRET_KEY: str = os.getenv('OBJECT_WEB_SECRET_KEY', 'SyRR1s7WKeav9WFmjtJuwACZNvYcl5S8vryr7uLz')
    OBJECT_BUCKET_NAME: str = os.getenv('OBJECT_BUCKET_NAME', 'test')

    # 處理相關配置
    DEFAULT_WORKER_COUNT: int = int(os.getenv('DEFAULT_WORKER_COUNT', '4'))
    MAX_WORKER_COUNT: int = int(os.getenv('MAX_WORKER_COUNT', '8'))
    MIN_WORKER_COUNT: int = int(os.getenv('MIN_WORKER_COUNT', '1'))

    # 檔案大小限制 (bytes)
    DEFAULT_FILE_SIZE_LIMIT: int = int(os.getenv('DEFAULT_FILE_SIZE_LIMIT', str(1 * 1024 * 1024)))  # 1MB
    SMALL_FILE_SIZE_LIMIT: int = int(os.getenv('SMALL_FILE_SIZE_LIMIT', str(100 * 1024)))  # 100KB
    MEDIUM_FILE_SIZE_LIMIT: int = int(os.getenv('MEDIUM_FILE_SIZE_LIMIT', str(550 * 1024)))  # 550KB
    LARGE_FILE_SIZE_LIMIT: int = int(os.getenv('LARGE_FILE_SIZE_LIMIT', str(800 * 1024)))  # 800KB

    # 字元偏移量
    CHAR_OFFSET: int = 95  # a = 97，b = 98，a:2 b:3

    # 排除的 DICOM 標籤
    EXCLUDE_DICOM_TAGS: dict[str, str] = {
        '00020012': 'Implementation Class UID',
        '00020013': 'Implementation Version Name',
        '00080005': 'Specific Character Set',
        '00080008': 'Image Type',
        '00080016': 'SOP Class UID',
        '00080020': 'Study Date',
        '00080021': 'Series Date',
        '00080022': 'Acquisition Date',
        '00080023': 'Study Date',
        '00080030': 'Study Time',
        '00080031': 'Series Time',
        '00080032': 'Acquisition Time',
        '00080033': 'Study Time',
        '00080050': 'Accession Number',
        '00080060': 'Modality',
        '00080070': 'Manufacturer',
        '00080080': 'Institution Name',
        '00080090': 'Referring Physician Name',
        '00081010': 'Station Name',
        '00081030': 'Study Description',
        '0008103e': 'Series Description',
        '00081090': 'Manufacturer Model Name',
        '00081111': 'Referenced Performed Procedure Step Sequence',
        '00081140': 'Referenced Image Sequence',
        '00082218': 'Anatomic Region Sequence',
        '00100010': 'Patient Name',
        '00100020': 'Patient ID',
        '00100030': 'Patient Birth Date',
        '00100040': 'Patient Sex',
        '00101010': 'Patient Age',
        '00101030': 'Patient Weight',
        '001021b0': 'Additional Patient History',
        '00180015': 'Body Part Examined',
        '00180020': 'Scanning Sequence',
        '00180021': 'Sequence Variant',
        '00180022': 'Scan Options',
        '00180023': 'MR Acquisition Type',
        '00180025': 'Angio Flag',
        '00181020': 'Software Versions',
        '00181030': 'Protocol Name',
        '0020000D': 'Study Instance UID',
        '0020000E': 'Series Instance UID',
        '00200010': 'Study ID',
        '00200011': 'Series Number',
        '00200012': 'Acquisition Number',
        '00210010': 'Private Creator',
        '00230010': 'Private Creator',
        '00231080': 'Private Creator',
        '00250010': 'Private Creator',
        '00270010': 'Private Creator',
        '00290010': 'Private Creator',
        '00380010': 'Admission ID',
        '00400242': 'Performed Station Name',
        '00400243': 'Performed Location',
        '00400244': 'Performed Procedure Step Start Date',
        '00400245': 'Performed Procedure Step Start Time',
        '00400252': 'Performed Procedure Step ID',
        '00400254': 'Performed Procedure Step Descriptio',
        '00400275': 'Request Attributes Sequence',
    }

    @classmethod
    def get_worker_count(cls, requested_count: int) -> int:
        """獲取有效的工作執行緒數量"""
        return min(cls.MAX_WORKER_COUNT, max(cls.MIN_WORKER_COUNT, requested_count))

    @classmethod
    def validate_path(cls, path: Optional[str]) -> Optional[Path]:
        """驗證並轉換路徑"""
        if path is None:
            return None
        path_obj = Path(path)
        if not path_obj.exists():
            raise FileNotFoundError(f"路徑不存在: {path}")
        return path_obj

    @classmethod
    def get_config_dict(cls) -> dict[str, Any]:
        """獲取所有配置作為字典"""
        return {
            'sql_web_url': cls.SQL_WEB_URL,
            'object_web_url': cls.OBJECT_WEB_URL,
            'object_web_access_key': cls.OBJECT_WEB_ACCESS_KEY,
            'object_web_secret_key': cls.OBJECT_WEB_SECRET_KEY,
            'object_bucket_name': cls.OBJECT_BUCKET_NAME,
            'default_worker_count': cls.DEFAULT_WORKER_COUNT,
            'max_worker_count': cls.MAX_WORKER_COUNT,
            'min_worker_count': cls.MIN_WORKER_COUNT,
            'default_file_size_limit': cls.DEFAULT_FILE_SIZE_LIMIT,
            'small_file_size_limit': cls.SMALL_FILE_SIZE_LIMIT,
            'medium_file_size_limit': cls.MEDIUM_FILE_SIZE_LIMIT,
            'large_file_size_limit': cls.LARGE_FILE_SIZE_LIMIT,
            'char_offset': cls.CHAR_OFFSET,
        }
