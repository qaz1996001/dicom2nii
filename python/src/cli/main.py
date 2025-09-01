"""
重構後的主要入口點
"""

import argparse
import sys

from ..core.exceptions import ConfigurationError, Dicom2NiiError
from .commands import (
    BaseCommand,
    DicomToNiftiCommand,
    NiftiToDicomCommand,
    ReportCommand,
    UploadCommand,
)


def create_parser() -> argparse.ArgumentParser:
    """建立主要的參數解析器"""
    parser = argparse.ArgumentParser(
        prog="dicom2nii",
        description="DICOM 和 NIfTI 檔案轉換工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # DICOM 到 NIfTI 轉換
  python -m src.cli.main convert --input_dicom /path/to/dicom --output_nifti /path/to/nifti

  # NIfTI 到 DICOM 轉換
  python -m src.cli.main nifti2dicom --input_nifti /path/to/nifti --output_dicom /path/to/dicom

  # 上傳檔案
  python -m src.cli.main upload --input /path/to/files --upload_all

  # 生成報告
  python -m src.cli.main report --input /path/to/data --type both
        """,
    )

    # 添加子命令
    subparsers = parser.add_subparsers(dest="command", help="可用的命令")

    # 註冊命令
    commands: dict[str, type[BaseCommand]] = {
        "convert": DicomToNiftiCommand,
        "nifti2dicom": NiftiToDicomCommand,
        "upload": UploadCommand,
        "report": ReportCommand,
    }

    for command_name, command_class in commands.items():
        command_parser = subparsers.add_parser(
            command_name, help=f"{command_name} 命令"
        )
        command_instance = command_class()
        command_instance.add_arguments(command_parser)
        command_parser.set_defaults(command_handler=command_instance)

    return parser


def main() -> None:
    """主要入口點函數"""
    try:
        # 建立解析器
        parser = create_parser()

        # 解析參數
        args = parser.parse_args()

        # 檢查是否提供了命令
        if not hasattr(args, "command_handler"):
            parser.print_help()
            sys.exit(1)

        # 執行命令
        args.command_handler.handle(args)

    except ConfigurationError as e:
        print(f"配置錯誤: {e.message}")
        if e.details:
            print(f"詳細資訊: {e.details}")
        sys.exit(1)

    except Dicom2NiiError as e:
        print(f"執行錯誤: {e.message}")
        if e.details:
            print(f"詳細資訊: {e.details}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n使用者中斷執行")
        sys.exit(1)

    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
