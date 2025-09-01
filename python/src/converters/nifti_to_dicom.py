"""
NIfTI 到 DICOM 轉換器
"""

import os
import re
from pathlib import Path
from typing import Optional

import nibabel as nib
import numpy as np
import orjson
from pydicom import Dataset

from ..core.enums import MRSeriesRenameEnum
from ..core.exceptions import ConversionError
from ..core.types import ExecutorType
from .base import BaseConverter


class NiftiToDicomConverter(BaseConverter):
    """NIfTI 到 DICOM 轉換器"""

    study_folder_name_pattern = re.compile(
        r"^(\d{8})_(\d{8})_(MR|CT)_(.*)$", re.IGNORECASE
    )

    def __init__(self, input_path: str, output_path: str):
        """初始化轉換器

        Args:
            input_path: 輸入 NIfTI 路徑
            output_path: 輸出 DICOM 路徑
        """
        super().__init__(input_path, output_path)

        # 設定預設排除集合
        self.exclude_set = {
            MRSeriesRenameEnum.MRAVR_BRAIN.value,
            MRSeriesRenameEnum.MRAVR_NECK.value,
            MRSeriesRenameEnum.DTI32D.value,
            MRSeriesRenameEnum.DTI64D.value,
            MRSeriesRenameEnum.RESTING.value,
            MRSeriesRenameEnum.RESTING2000.value,
        }

    def convert(self, executor: ExecutorType = None) -> None:
        """執行 NIfTI 到 DICOM 轉換

        Args:
            executor: 執行器，用於並行處理
        """
        try:
            # 檢查輸入路徑結構
            items = list(self.input_path.iterdir())
            is_all_directories = all(item.is_dir() for item in items)

            if is_all_directories:
                # 處理多個檢查
                for study_path in items:
                    self._convert_study(study_path)
            else:
                # 處理單一檢查
                self._convert_study(self.input_path)

        except Exception as e:
            raise ConversionError(f"NIfTI 到 DICOM 轉換失敗: {str(e)}")

    def _convert_study(self, study_path: Path) -> None:
        """轉換單一檢查"""
        try:
            # 尋找所有 NIfTI 檔案
            nifti_files = [
                f for f in study_path.iterdir() if f.name.endswith(".nii.gz")
            ]

            for nifti_file in nifti_files:
                # 檢查是否應該排除
                if self._is_excluded(nifti_file.stem):
                    continue

                # 尋找對應的元資料檔案
                meta_file = self._find_meta_file(nifti_file)
                if not meta_file:
                    print(f"找不到元資料檔案: {nifti_file}")
                    continue

                # 執行轉換
                output_folder = self.output_path / study_path.name / nifti_file.stem
                self._convert_nifti_to_dicom(nifti_file, meta_file, output_folder)

        except Exception as e:
            raise ConversionError(f"轉換檢查失敗 {study_path}: {str(e)}")

    def _find_meta_file(self, nifti_file: Path) -> Optional[Path]:
        """尋找對應的元資料檔案"""
        meta_folder = nifti_file.parent / ".meta"
        if not meta_folder.exists():
            return None

        meta_file_name = nifti_file.name.replace(".nii.gz", ".jsonlines")
        meta_file = meta_folder / meta_file_name

        return meta_file if meta_file.exists() else None

    def _convert_nifti_to_dicom(
        self, nifti_file: Path, meta_file: Path, output_folder: Path
    ) -> None:
        """轉換單一 NIfTI 檔案到 DICOM"""
        try:
            # 跳過冠狀面和矢狀面
            if "COR" in nifti_file.name or "SAG" in nifti_file.name:
                return

            # 載入 NIfTI 檔案
            nifti_obj = nib.load(str(nifti_file))
            nifti_array = nifti_obj.get_fdata().round(0).astype(np.int16)

            # 處理影像方向
            nifti_array = self._handle_image_orientation(nifti_obj, nifti_array)

            # 載入元資料
            dicom_headers = self._load_dicom_headers(meta_file, nifti_array.shape[0])

            # 建立輸出目錄
            os.makedirs(output_folder, exist_ok=True)

            # 生成 DICOM 檔案
            self._generate_dicom_files(dicom_headers, nifti_array, output_folder)

        except Exception as e:
            raise ConversionError(f"轉換 NIfTI 到 DICOM 失敗 {nifti_file}: {str(e)}")

    def _handle_image_orientation(
        self, nifti_obj: nib.Nifti1Image, nifti_array: np.ndarray
    ) -> np.ndarray:
        """處理影像方向"""
        try:
            nifti_obj_axcodes = tuple(nib.aff2axcodes(nifti_obj.affine))
            pixdim = nifti_obj.header.get("pixdim")

            if pixdim[0] == -1:
                nifti_array = self._do_reorientation(
                    nifti_array, nifti_obj_axcodes, ("S", "P", "L")
                )
            elif pixdim[0] == 1 and nifti_obj_axcodes == ("R", "A", "S"):
                nifti_array = self._do_reorientation(
                    nifti_array, nifti_obj_axcodes, ("S", "P", "L")
                )

            return nifti_array

        except Exception as e:
            raise ConversionError(f"影像方向處理失敗: {str(e)}")

    def _load_dicom_headers(
        self, meta_file: Path, expected_slices: int
    ) -> list[Dataset]:
        """載入 DICOM 標頭資訊"""
        try:
            with open(meta_file, encoding="utf8") as file:
                orjson_dict = orjson.loads(file.read())

            exclude_tags = {"0018A001", "00081070", "00081110"}
            dicom_headers = []

            for _key, value in orjson_dict.items():
                if len(value) == expected_slices:
                    # 處理第一個標頭
                    dicom_headers.append(Dataset.from_json(value[0]))

                    # 處理其餘標頭
                    for i in range(1, len(value)):
                        temp_header = Dataset.from_json(value[0])
                        temp_data = value[i]

                        for tag_key, tag_value in temp_data.items():
                            if tag_key in exclude_tags:
                                continue

                            idx_1 = int(tag_key[:4], base=16)
                            idx_2 = int(tag_key[4:], base=16)
                            temp_header[idx_1, idx_2].value = tag_value

                        dicom_headers.append(temp_header)
                    break

            if not dicom_headers:
                raise ConversionError("無法載入 DICOM 標頭資訊")

            # 排序標頭
            return self._sort_dicom_headers(dicom_headers)

        except Exception as e:
            raise ConversionError(f"載入 DICOM 標頭失敗: {str(e)}")

    def _sort_dicom_headers(self, headers: list[Dataset]) -> list[Dataset]:
        """排序 DICOM 標頭"""
        try:
            # 嘗試按影像位置排序
            if headers[0].get((0x0020, 0x0032)):
                return sorted(headers, key=lambda x: x[0x0020, 0x0032].value[-1])
            else:
                # 按實例編號排序
                return sorted(headers, key=lambda x: x[0x0020, 0x0013].value)
        except Exception:
            return headers  # 如果排序失敗，返回原始順序

    def _generate_dicom_files(
        self, headers: list[Dataset], nifti_array: np.ndarray, output_folder: Path
    ) -> None:
        """生成 DICOM 檔案"""
        try:
            for i, header in enumerate(headers):
                if i >= nifti_array.shape[0]:
                    break

                # 設定像素資料
                slice_data = nifti_array[i]
                header.PixelData = slice_data.tobytes()
                header.is_little_endian = True
                header.is_implicit_VR = True

                # 儲存 DICOM 檔案
                output_file = output_folder / f"{header.SOPInstanceUID}.dcm"
                header.save_as(str(output_file))

        except Exception as e:
            raise ConversionError(f"生成 DICOM 檔案失敗: {str(e)}")

    @classmethod
    def _compute_orientation(cls, init_axcodes: tuple, final_axcodes: tuple) -> tuple:
        """計算方向轉換"""
        ornt_init = nib.orientations.axcodes2ornt(init_axcodes)
        ornt_fin = nib.orientations.axcodes2ornt(final_axcodes)
        ornt_transf = nib.orientations.ornt_transform(ornt_init, ornt_fin)
        return ornt_transf, ornt_init, ornt_fin

    @classmethod
    def _do_reorientation(
        cls, data_array: np.ndarray, init_axcodes: tuple, final_axcodes: tuple
    ) -> np.ndarray:
        """執行影像重新定向"""
        ornt_transf, ornt_init, ornt_fin = cls._compute_orientation(
            init_axcodes, final_axcodes
        )

        if np.array_equal(ornt_init, ornt_fin):
            return data_array

        return nib.orientations.apply_orientation(data_array, ornt_transf)
