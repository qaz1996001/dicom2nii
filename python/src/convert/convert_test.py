import argparse
import os
import pathlib

if __name__ == "__main__":
    # input_path = r'D:\00_Chen\Task08\data\Study_Glymphatics\20230525_10671432_COVID Study'
    # output_path = r'D:\00_Chen\Task08\data\rename_dicom_processing_strategy_0103'

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dicom",
        dest="input_dicom",
        type=str,
        required=True,
        help="input the raw dicom folder.\r\n",
    )
    parser.add_argument(
        "--output_dicom",
        dest="output_dicom",
        type=str,
        required=True,
        help="output the rename dicom folder.\r\n",
    )
    parser.add_argument(
        "--output_nifti",
        dest="output_nifti",
        type=str,
        required=True,
        help="rename dicom output to nifti folder.\r\n"
        "Example ： python convert.py --input_dicom raw_dicom_path --output_dicom rename_dicom_path "
        "--output_nifti output_nifti_path",
    )
    parser.add_argument(
        "--work",
        dest="work",
        type=int,
        default=4,
        help="Thread cont .\r\n"
        "Example ： python convert.py --input_dicom raw_dicom_path --output_dicom rename_dicom_path "
        "--output_nifti output_nifti_path --work 8",
    )
    args = parser.parse_args()
    input_dicom_path = args.input_dicom
    output_dicom_path = args.output_dicom
    output_nifti_path = args.output_nifti
    work_count = args.work
    file_path = pathlib.Path(__file__).absolute().parent
    rename_folder_cmd = f'python {str(file_path.joinpath("dicom_rename_mr.py"))} --input "{input_dicom_path}" --output "{output_dicom_path}" --work {work_count}'
    convert_nifti_cmd = f'python {str(file_path.joinpath("convert_nifti.py"))} --input "{output_dicom_path}" --output "{output_nifti_path}" --work {work_count}'
    convert_nifti_postprocess_cmd = f'python {str(file_path.joinpath("convert_nifti_postprocess.py"))} --input "{output_nifti_path}"'
    list_nii_cmd = (
        f'python {str(file_path.joinpath("list_nii.py"))} --input "{output_nifti_path}"'
    )
    list_dicom_cmd = f'python {str(file_path.joinpath("list_dicom.py"))} --input "{output_dicom_path}"'

    print(file_path)
    # print(rename_folder_cmd)
    # os.system(rename_folder_cmd)
    # rename_folder_process = subprocess.run(rename_folder_cmd, capture_output=True)
    print(list_dicom_cmd)
    # os.system(list_dicom_cmd)

    print(convert_nifti_cmd)
    # convert_nifti_process = subprocess.run(convert_nifti_cmd, capture_output=True)
    os.system(convert_nifti_cmd)
    print(convert_nifti_postprocess_cmd)
    os.system(convert_nifti_postprocess_cmd)
    print(list_nii_cmd)
    os.system(list_nii_cmd)
