"""
檔案操作工具函數
"""

import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional

from ..core.exceptions import FileOperationError
from ..core.types import PathLike


def create_directory(path: PathLike, exist_ok: bool = True) -> Path:
    """安全地建立目錄"""
    try:
        path_obj = Path(path)
        path_obj.mkdir(parents=True, exist_ok=exist_ok)
        return path_obj
    except Exception as e:
        raise FileOperationError(f"無法建立目錄 {path}: {str(e)}")


def get_file_size(file_path: PathLike) -> int:
    """獲取檔案大小"""
    try:
        return Path(file_path).stat().st_size
    except Exception as e:
        raise FileOperationError(f"無法獲取檔案大小 {file_path}: {str(e)}")


@contextmanager
def safe_file_operation(operation_name: str):
    """安全的檔案操作上下文管理器"""
    try:
        yield
    except Exception as e:
        raise FileOperationError(f"{operation_name} 操作失敗: {str(e)}")


def copy_directory_tree(
    src: PathLike, dst: PathLike, dirs_exist_ok: bool = True
) -> None:
    """複製目錄樹"""
    try:
        shutil.copytree(src, dst, dirs_exist_ok=dirs_exist_ok)
    except Exception as e:
        raise FileOperationError(f"複製目錄失敗 {src} -> {dst}: {str(e)}")


def move_file(src: PathLike, dst: PathLike) -> None:
    """移動檔案"""
    try:
        src_path = Path(src)
        dst_path = Path(dst)

        # 確保目標目錄存在
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        src_path.rename(dst_path)
    except Exception as e:
        raise FileOperationError(f"移動檔案失敗 {src} -> {dst}: {str(e)}")


def delete_file(file_path: PathLike, missing_ok: bool = True) -> None:
    """安全地刪除檔案"""
    try:
        path_obj = Path(file_path)
        if path_obj.exists():
            path_obj.unlink()
        elif not missing_ok:
            raise FileNotFoundError(f"檔案不存在: {file_path}")
    except Exception as e:
        if not missing_ok:
            raise FileOperationError(f"刪除檔案失敗 {file_path}: {str(e)}")


def find_files_by_pattern(
    directory: PathLike, pattern: str, recursive: bool = True
) -> list[Path]:
    """根據模式尋找檔案"""
    try:
        dir_path = Path(directory)
        if recursive:
            return list(dir_path.rglob(pattern))
        else:
            return list(dir_path.glob(pattern))
    except Exception as e:
        raise FileOperationError(f"尋找檔案失敗 {directory}/{pattern}: {str(e)}")


def get_directory_structure(
    directory: PathLike, max_depth: Optional[int] = None
) -> dict[str, Any]:
    """獲取目錄結構"""

    def _build_structure(path: Path, current_depth: int = 0) -> dict[str, Any]:
        if max_depth is not None and current_depth >= max_depth:
            return {}

        structure = {"type": "directory", "children": {}}

        try:
            for item in path.iterdir():
                if item.is_file():
                    structure["children"][item.name] = {
                        "type": "file",
                        "size": item.stat().st_size,
                    }
                elif item.is_dir():
                    structure["children"][item.name] = _build_structure(
                        item, current_depth + 1
                    )
        except PermissionError:
            structure["error"] = "Permission denied"

        return structure

    try:
        return _build_structure(Path(directory))
    except Exception as e:
        raise FileOperationError(f"獲取目錄結構失敗 {directory}: {str(e)}")
