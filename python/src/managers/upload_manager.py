"""
上傳管理器
"""

from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Optional, Union

import requests

from ..core.config import Config
from ..core.exceptions import UploadError
from ..core.types import ExecutorType
from .base import BaseManager


class UploadManager(BaseManager):
    """統一的上傳管理器"""

    def __init__(self,
                 input_path: Union[str, Path],
                 web_url: Optional[str] = None,
                 worker_count: int = Config.DEFAULT_WORKER_COUNT):
        """初始化上傳管理器

        Args:
            input_path: 輸入路徑
            web_url: Web API URL
            worker_count: 工作執行緒數量
        """
        super().__init__(input_path)

        self.web_url = web_url or Config.SQL_WEB_URL
        self.worker_count = self._validate_worker_count(worker_count)

    def run(self, executor: ExecutorType = None) -> None:
        """執行上傳流程

        Args:
            executor: 執行器，用於並行處理
        """
        try:
            study_paths = self._get_study_paths()

            # 執行上傳
            if executor:
                self._upload_with_executor(study_paths, executor)
            else:
                with self._create_executor(self.worker_count) as upload_executor:
                    self._upload_with_executor(study_paths, upload_executor)

        except Exception as e:
            raise UploadError(f"上傳管理器執行失敗: {str(e)}")

    def _upload_with_executor(self, study_paths: list[Path], executor: ThreadPoolExecutor) -> None:
        """使用執行器進行並行上傳"""
        futures: list[Future] = []

        for study_path in study_paths:
            future = executor.submit(self._upload_study, study_path)
            futures.append(future)

        # 等待所有上傳完成
        for future in futures:
            try:
                future.result()
            except Exception as e:
                self._handle_processing_error(e, "上傳檢查失敗")

    def _upload_study(self, study_path: Path) -> None:
        """上傳單一檢查"""
        try:
            self._log_progress("開始上傳", study_path.name)

            # 上傳目錄中的檔案
            for item in study_path.iterdir():
                if item.is_dir():
                    # 上傳目錄中的所有檔案
                    for file_path in item.iterdir():
                        self._upload_file_metadata(study_path, file_path, is_nested=True)
                elif item.is_file():
                    # 直接上傳檔案
                    self._upload_file_metadata(study_path, item, is_nested=False)

            self._log_progress("上傳完成", study_path.name)

        except Exception as e:
            raise UploadError(f"上傳檢查失敗 {study_path}: {str(e)}")

    def _upload_file_metadata(self, study_path: Path, file_path: Path, is_nested: bool = True) -> None:
        """上傳檔案元資料到 SQL

        Args:
            study_path: 檢查路徑
            file_path: 檔案路徑
            is_nested: 是否為巢狀結構
        """
        try:
            # 建構檔案 URL
            if is_nested:
                file_url = f'{study_path.name}/{file_path.parent.name}/{file_path.name}'
            else:
                file_url = f'{study_path.name}/{file_path.name}'

            self._log_progress(f"上傳檔案: {file_url}")

            # 準備上傳資料
            files = {'file': open(file_path, 'rb')}
            form_data = {'file_url': file_url}

            # 發送請求
            with requests.Session() as session:
                response = session.post(
                    url=f'{self.web_url}file/',
                    files=files,
                    data=form_data,
                    timeout=30
                )

                if response.status_code != 200:
                    raise UploadError(f"上傳失敗，狀態碼: {response.status_code}")

                print(f"上傳成功: {file_url}")

        except Exception as e:
            raise UploadError(f"上傳檔案元資料失敗 {file_path}: {str(e)}")
        finally:
            # 確保檔案被關閉
            if 'files' in locals():
                files['file'].close()

    def upload_nifti_files(self, executor: ExecutorType = None) -> None:
        """專門上傳 NIfTI 檔案"""
        try:
            study_paths = self._get_study_paths()

            for study_path in study_paths:
                nifti_files = list(study_path.rglob('*.nii.gz'))

                for nifti_file in nifti_files:
                    self._upload_file_metadata(
                        study_path,
                        nifti_file,
                        is_nested=nifti_file.parent != study_path
                    )

        except Exception as e:
            raise UploadError(f"上傳 NIfTI 檔案失敗: {str(e)}")

    def upload_dicom_files(self, executor: ExecutorType = None) -> None:
        """專門上傳 DICOM 檔案"""
        try:
            study_paths = self._get_study_paths()

            for study_path in study_paths:
                dicom_files = list(study_path.rglob('*.dcm'))

                for dicom_file in dicom_files:
                    self._upload_file_metadata(
                        study_path,
                        dicom_file,
                        is_nested=dicom_file.parent != study_path
                    )

        except Exception as e:
            raise UploadError(f"上傳 DICOM 檔案失敗: {str(e)}")


class SqlUploadManager(BaseManager):
    """SQL 上傳管理器"""

    def __init__(self, input_path: Union[str, Path]):
        """初始化 SQL 上傳管理器

        Args:
            input_path: 輸入路徑
        """
        super().__init__(input_path)
        self.web_url = Config.SQL_WEB_URL

    def run(self, executor: ExecutorType = None) -> None:
        """執行 SQL 上傳

        Args:
            executor: 執行器，用於並行處理
        """
        try:
            study_paths = self._get_study_paths()

            for study_path in study_paths:
                self._process_study_metadata(study_path)

        except Exception as e:
            raise UploadError(f"SQL 上傳管理器執行失敗: {str(e)}")

    def _process_study_metadata(self, study_path: Path) -> None:
        """處理檢查元資料"""
        try:
            # 尋找 .nii.gz 檔案和對應的元資料
            nifti_files = [f for f in study_path.iterdir() if f.name.endswith('.nii.gz')]

            for nifti_file in nifti_files:
                meta_file = self._find_corresponding_meta_file(nifti_file)
                if meta_file:
                    self._log_progress(f"處理元資料: {nifti_file.name}")
                    # 這裡可以添加具體的元資料處理邏輯

        except Exception as e:
            raise UploadError(f"處理檢查元資料失敗 {study_path}: {str(e)}")

    def _find_corresponding_meta_file(self, nifti_file: Path) -> Optional[Path]:
        """尋找對應的元資料檔案"""
        meta_folder = nifti_file.parent / '.meta'
        if not meta_folder.exists():
            return None

        meta_file_name = nifti_file.name.replace('.nii.gz', '.jsonlines')
        meta_file = meta_folder / meta_file_name

        return meta_file if meta_file.exists() else None
