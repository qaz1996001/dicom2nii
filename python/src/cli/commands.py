"""
命令列命令定義
"""

import argparse
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional

from src.core.config import Config
from src.core.exceptions import ConfigurationError
from src.managers import ConvertManager, UploadManager
from src.utils.reporting import generate_nifti_report, generate_study_report


class BaseCommand(metaclass=ABCMeta):
    """命令基礎類別"""

    @abstractmethod
    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """添加命令參數"""
        pass

    @abstractmethod
    def handle(self, args: argparse.Namespace) -> None:
        """處理命令"""
        pass

    def validate_path(
        self, path: Optional[str], required: bool = True, must_exist: bool = True
    ) -> Optional[Path]:
        """驗證路徑"""
        if path is None:
            if required:
                raise ConfigurationError("必要的路徑參數未提供")
            return None

        path_obj = Path(path)

        # 只有在 must_exist=True 且 required=True 時才檢查路徑存在性
        if required and must_exist and not path_obj.exists():
            raise ConfigurationError(f"路徑不存在: {path}")

        return path_obj


class DicomToNiftiCommand(BaseCommand):
    """DICOM 到 NIfTI 轉換命令"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """添加 DICOM 到 NIfTI 轉換的參數"""
        parser.add_argument(
            "--input_dicom",
            dest="input_dicom",
            type=str,
            required=True,
            help="輸入的原始 DICOM 資料夾路徑",
        )
        parser.add_argument(
            "--output_dicom",
            dest="output_dicom",
            type=str,
            help="輸出的重新命名 DICOM 資料夾路徑",
        )
        parser.add_argument(
            "--output_nifti",
            dest="output_nifti",
            type=str,
            help="重新命名 DICOM 輸出到 NIfTI 資料夾路徑",
        )
        parser.add_argument(
            "--work",
            dest="work",
            type=int,
            default=Config.DEFAULT_WORKER_COUNT,
            help=f"執行緒數量 (預設: {Config.DEFAULT_WORKER_COUNT}，最大: {Config.MAX_WORKER_COUNT})",
        )

    def handle(self, args: argparse.Namespace) -> None:
        """處理 DICOM 到 NIfTI 轉換命令"""
        try:
            # 驗證路徑
            input_dicom_path = self.validate_path(
                args.input_dicom, required=True, must_exist=True
            )
            output_dicom_path = self.validate_path(
                args.output_dicom, required=False, must_exist=False
            )
            output_nifti_path = self.validate_path(
                args.output_nifti, required=False, must_exist=False
            )

            if not output_dicom_path and not output_nifti_path:
                raise ConfigurationError("至少需要提供一個輸出路徑")

            # 建立轉換管理器
            convert_manager = ConvertManager(
                input_path=input_dicom_path,
                output_dicom_path=output_dicom_path,
                output_nifti_path=output_nifti_path,
                worker_count=args.work,
            )

            # 執行轉換
            convert_manager.run()

            # 顯示統計資訊
            stats = convert_manager.get_conversion_statistics()
            print("轉換統計:")
            for key, value in stats.items():
                print(f"  {key}: {value}")

        except Exception as e:
            raise ConfigurationError(f"DICOM 到 NIfTI 轉換命令失敗: {str(e)}")


class NiftiToDicomCommand(BaseCommand):
    """NIfTI 到 DICOM 轉換命令"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """添加 NIfTI 到 DICOM 轉換的參數"""
        parser.add_argument(
            "--input_nifti",
            dest="input_nifti",
            type=str,
            required=True,
            help="輸入的 NIfTI 資料夾路徑",
        )
        parser.add_argument(
            "--output_dicom",
            dest="output_dicom",
            type=str,
            required=True,
            help="輸出的 DICOM 資料夾路徑",
        )
        parser.add_argument(
            "--work",
            dest="work",
            type=int,
            default=Config.DEFAULT_WORKER_COUNT,
            help=f"執行緒數量 (預設: {Config.DEFAULT_WORKER_COUNT})",
        )

    def handle(self, args: argparse.Namespace) -> None:
        """處理 NIfTI 到 DICOM 轉換命令"""
        try:
            # 驗證路徑
            input_nifti_path = self.validate_path(
                args.input_nifti, required=True, must_exist=True
            )
            output_dicom_path = self.validate_path(
                args.output_dicom, required=False, must_exist=False
            )

            # 建立轉換管理器
            convert_manager = ConvertManager(
                input_path=input_nifti_path,
                output_dicom_path=output_dicom_path,
                worker_count=args.work,
            )

            # 執行轉換
            convert_manager.run()

        except Exception as e:
            raise ConfigurationError(f"NIfTI 到 DICOM 轉換命令失敗: {str(e)}")


class UploadCommand(BaseCommand):
    """上傳命令"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """添加上傳的參數"""
        parser.add_argument(
            "--input", dest="input", type=str, required=True, help="輸入資料夾路徑"
        )
        parser.add_argument(
            "--upload_nifti",
            dest="upload_nifti",
            action="store_true",
            help="上傳 NIfTI 檔案到 SQL 和物件儲存",
        )
        parser.add_argument(
            "--upload_dicom",
            dest="upload_dicom",
            action="store_true",
            help="上傳 DICOM 檔案到 NAS",
        )
        parser.add_argument(
            "--upload_all", dest="upload_all", action="store_true", help="上傳所有檔案"
        )
        parser.add_argument(
            "--work",
            dest="work",
            type=int,
            default=Config.DEFAULT_WORKER_COUNT,
            help=f"執行緒數量 (預設: {Config.DEFAULT_WORKER_COUNT})",
        )

    def handle(self, args: argparse.Namespace) -> None:
        """處理上傳命令"""
        try:
            # 驗證路徑
            input_path = self.validate_path(args.input, required=True, must_exist=True)

            # 建立上傳管理器
            upload_manager = UploadManager(
                input_path=input_path, worker_count=args.work
            )

            # 根據參數決定上傳類型
            if args.upload_all:
                upload_manager.run()
            elif args.upload_nifti:
                upload_manager.upload_nifti_files()
            elif args.upload_dicom:
                upload_manager.upload_dicom_files()
            else:
                print("請指定上傳類型: --upload_nifti, --upload_dicom, 或 --upload_all")

        except Exception as e:
            raise ConfigurationError(f"上傳命令失敗: {str(e)}")


class ReportCommand(BaseCommand):
    """報告生成命令"""

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        """添加報告生成的參數"""
        parser.add_argument(
            "--input", dest="input", type=str, required=True, help="輸入資料夾路徑"
        )
        parser.add_argument(
            "--type",
            dest="report_type",
            choices=["dicom", "nifti", "both"],
            default="both",
            help="報告類型 (預設: both)",
        )
        parser.add_argument(
            "--format",
            dest="output_format",
            choices=["excel", "csv", "both"],
            default="both",
            help="輸出格式 (預設: both)",
        )

    def handle(self, args: argparse.Namespace) -> None:
        """處理報告生成命令"""
        try:
            # 驗證路徑
            input_path = self.validate_path(args.input, required=True, must_exist=True)

            # 生成報告
            if args.report_type in ["dicom", "both"]:
                print("生成 DICOM 報告...")
                generate_study_report(input_path, args.output_format)

            if args.report_type in ["nifti", "both"]:
                print("生成 NIfTI 報告...")
                generate_nifti_report(input_path, args.output_format)

            print("報告生成完成")

        except Exception as e:
            raise ConfigurationError(f"報告生成命令失敗: {str(e)}")
