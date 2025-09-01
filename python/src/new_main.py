"""
新的主要入口點 - 向後相容的介面
"""

import argparse
import sys
from pathlib import Path

# 添加當前目錄到 Python 路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from cli.main import main as cli_main
    from core.config import Config
    from core.exceptions import Dicom2NiiError
    from managers import ConvertManager, UploadManager
except ImportError:
    # 如果相對匯入失敗，嘗試絕對匯入
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.cli.main import main as cli_main
    from src.core.config import Config
    from src.core.exceptions import Dicom2NiiError
    from src.managers import ConvertManager, UploadManager


def parse_legacy_arguments() -> argparse.Namespace:
    """解析舊版本的命令列參數 (向後相容)"""
    parser = argparse.ArgumentParser(
        description='DICOM2NII 轉換工具 (舊版相容介面)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # 保持與原始 main.py 相同的參數
    parser.add_argument(
        '--input_dicom',
        dest='input_dicom',
        type=str,
        help="輸入的原始 DICOM 資料夾"
    )
    parser.add_argument(
        '--output_dicom',
        dest='output_dicom',
        type=str,
        help="輸出的重新命名 DICOM 資料夾"
    )
    parser.add_argument(
        '--output_nifti',
        dest='output_nifti',
        type=str,
        help="重新命名 DICOM 輸出到 NIfTI 資料夾"
    )
    parser.add_argument(
        '--work',
        dest='work',
        type=int,
        default=Config.DEFAULT_WORKER_COUNT,
        help="執行緒數量"
    )
    parser.add_argument(
        '--upload_all',
        dest='upload_all',
        type=str,
        help="上傳所有檔案"
    )
    parser.add_argument(
        '--upload_nifti',
        dest='upload_nifti',
        type=str,
        help="上傳重新命名的 NIfTI 資料夾到 SQL 和物件儲存"
    )
    parser.add_argument(
        '--upload_dicom',
        dest='upload_dicom',
        type=str,
        help="上傳重新命名的 DICOM 所有檔案到 NAS"
    )

    return parser.parse_args()


def run_legacy_workflow(args: argparse.Namespace) -> None:
    """執行舊版本的工作流程"""
    try:
        # DICOM 處理和轉換
        if args.input_dicom and args.output_dicom:
            print("執行 DICOM 重新命名和處理...")

            # 建立轉換管理器
            convert_manager = ConvertManager(
                input_path=args.input_dicom,
                output_dicom_path=args.output_dicom,
                output_nifti_path=args.output_nifti,
                worker_count=args.work
            )

            # 執行轉換
            convert_manager.run()

        # NIfTI 轉換
        if args.output_dicom and args.output_nifti:
            print("執行 DICOM 到 NIfTI 轉換...")
            # 轉換邏輯已經在上面的 ConvertManager 中處理

        # 上傳處理
        upload_path = None
        if args.upload_all == 'True':
            upload_path = args.output_nifti or args.output_dicom
        elif args.upload_nifti == 'True':
            upload_path = args.output_nifti
        elif args.upload_dicom == 'True':
            upload_path = args.output_dicom

        if upload_path:
            print(f"執行檔案上傳: {upload_path}")
            upload_manager = UploadManager(
                input_path=upload_path,
                worker_count=args.work
            )
            upload_manager.run()

        print("所有處理完成")

    except Exception as e:
        raise Dicom2NiiError(f"舊版工作流程執行失敗: {str(e)}")


def main() -> None:
    """主要入口點"""
    try:
        # 檢查是否使用新的命令列介面
        if len(sys.argv) > 1 and sys.argv[1] in ['convert', 'nifti2dicom', 'upload', 'report']:
            # 使用新的 CLI
            cli_main()
        else:
            # 使用舊版相容介面
            args = parse_legacy_arguments()
            run_legacy_workflow(args)

    except Dicom2NiiError as e:
        print(f"錯誤: {e.message}")
        if e.details:
            print(f"詳細資訊: {e.details}")
        sys.exit(1)

    except Exception as e:
        print(f"未預期的錯誤: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
