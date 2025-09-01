"""
報告生成工具函數
"""

from pathlib import Path

import orjson
import pandas as pd
from pydicom import Dataset

from ..core.exceptions import FileOperationError
from ..core.types import PathLike
from .dicom_utils import extract_dicom_info


def generate_study_report(
    data_path: PathLike, output_format: str = "both"
) -> pd.DataFrame:
    """生成檢查報告"""
    try:
        data_path = Path(data_path)
        study_data = []

        for study_path in data_path.iterdir():
            if not study_path.is_dir():
                continue

            series_folders = [
                series_path
                for series_path in study_path.iterdir()
                if series_path.is_dir() and series_path.name != ".meta"
            ]

            for series_path in series_folders:
                study_data.append([study_path.name, series_path.name, 1])

        # 建立 DataFrame
        df = pd.DataFrame(study_data, columns=["study_id", "series_name", "count"])

        # 解析檢查 ID
        df["patient_id"] = df["study_id"].str.split("_").str[0]
        df["study_date"] = df["study_id"].str.split("_").str[1]
        df["accession_number"] = df["study_id"].str.split("_").str[-1]

        # 建立樞紐表
        pivot_df = df.pivot_table(
            index=["patient_id", "study_date", "accession_number"],
            columns="series_name",
            values="count",
            aggfunc="count",
            fill_value=0,
        )

        # 輸出檔案
        if output_format in ["excel", "both"]:
            excel_path = data_path.parent / f"{data_path.name}_study_report.xlsx"
            pivot_df.to_excel(excel_path, merge_cells=False, index=True)

        if output_format in ["csv", "both"]:
            csv_path = data_path.parent / f"{data_path.name}_study_report.csv"
            pivot_df.to_csv(csv_path, index=True)

        return pivot_df

    except Exception as e:
        raise FileOperationError(f"生成檢查報告失敗: {str(e)}") from e


def generate_series_report(
    data_path: PathLike, output_format: str = "both"
) -> pd.DataFrame:
    """生成序列報告"""
    try:
        data_path = Path(data_path)
        series_data = []

        for study_path in data_path.iterdir():
            if not study_path.is_dir():
                continue

            meta_folder = study_path / ".meta"
            if not meta_folder.exists():
                continue

            for meta_file in meta_folder.iterdir():
                if not meta_file.name.endswith(".jsonlines"):
                    continue

                try:
                    with open(meta_file, encoding="utf8") as file:
                        orjson_dict = orjson.loads(file.read())

                    for _key, value in orjson_dict.items():
                        if value:
                            dicom_header = Dataset.from_json(value[0])
                            data_dict = extract_dicom_info(dicom_ds=dicom_header)
                            data_dict["series_description"] = meta_file.stem
                            series_data.append(data_dict)

                except Exception as e:
                    print(f"處理 meta 檔案失敗 {meta_file}: {str(e)}")
                    continue

        # 建立 DataFrame
        df = pd.DataFrame(series_data)

        # 輸出檔案
        if output_format in ["excel", "both"]:
            excel_path = data_path.parent / f"{data_path.name}_series_report.xlsx"
            df.to_excel(excel_path, merge_cells=False, index=False)

        if output_format in ["csv", "both"]:
            csv_path = data_path.parent / f"{data_path.name}_series_report.csv"
            df.to_csv(csv_path, index=False)

        return df

    except Exception as e:
        raise FileOperationError(f"生成序列報告失敗: {str(e)}") from e


def generate_nifti_report(
    data_path: PathLike, output_format: str = "excel"
) -> pd.DataFrame:
    """生成 NIfTI 檔案報告"""
    try:
        data_path = Path(data_path)
        nifti_data = []

        for study_path in data_path.iterdir():
            if not study_path.is_dir():
                continue

            nifti_files = list(study_path.rglob("*.nii.gz"))

            for nifti_file in nifti_files:
                nifti_data.append([study_path.name, nifti_file.name, 1])

        # 建立 DataFrame
        df = pd.DataFrame(nifti_data, columns=["study_id", "series_name", "count"])

        # 解析檢查 ID
        df["patient_id"] = df["study_id"].str.split("_").str[0]
        df["study_date"] = df["study_id"].str.split("_").str[1]
        df["accession_number"] = df["study_id"].str.split("_").str[-1]

        # 建立樞紐表
        pivot_df = df.pivot_table(
            index=["patient_id", "study_date", "accession_number"],
            columns="series_name",
            values="count",
            aggfunc="count",
            fill_value=0,
        )

        # 輸出檔案
        if output_format in ["excel", "both"]:
            excel_path = data_path.parent / f"{data_path.name}_nifti_report.xlsx"
            pivot_df.to_excel(excel_path, merge_cells=False, index=True)

        if output_format in ["csv", "both"]:
            csv_path = data_path.parent / f"{data_path.name}_nifti_report.csv"
            pivot_df.to_csv(csv_path, index=True)

        return pivot_df

    except Exception as e:
        raise FileOperationError(f"生成 NIfTI 報告失敗: {str(e)}") from e


def create_processing_summary(
    processed_studies: list[str], failed_studies: list[str], output_path: PathLike
) -> None:
    """建立處理摘要報告"""
    try:
        summary = {
            "total_studies": len(processed_studies) + len(failed_studies),
            "successful_studies": len(processed_studies),
            "failed_studies": len(failed_studies),
            "success_rate": len(processed_studies)
            / (len(processed_studies) + len(failed_studies))
            * 100
            if (processed_studies or failed_studies)
            else 0,
            "processed_list": processed_studies,
            "failed_list": failed_studies,
        }

        output_file = Path(output_path) / "processing_summary.json"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(orjson.dumps(summary, option=orjson.OPT_INDENT_2).decode())

    except Exception as e:
        raise FileOperationError(f"建立處理摘要失敗: {str(e)}") from e
