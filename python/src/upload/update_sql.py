import argparse
import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import Union

from . import SQL_WEB_URL


class UploadSqlManager:
    url = SQL_WEB_URL

    def __init__(self, input_path: Union[str, pathlib.Path], *args, **kwargs):
        self._input_path = pathlib.Path(input_path)

    def get_patient_info(
        self,
    ):
        pass

    def get_study_info(
        self,
    ):
        pass

    def get_series_info(
        self,
    ):
        pass

    def make_series_file_mapping(
        self,
    ):
        pass

    def upload(self, study_path):
        meta_path = study_path.joinpath(".meta")
        list(meta_path.iterdir())
        for series_path in study_path.iterdir():
            if series_path.is_file():
                # nii.gz .meta/series.jsonline mapping
                if series_path.name.endswith("nii.gz"):
                    print(series_path)

            if series_path.is_dir():
                pass

    def run(self, executor: Union[ThreadPoolExecutor, None] = None):
        is_dir_flag = all(x.is_dir() for x in self.input_path.iterdir())
        if is_dir_flag:
            study_path_list = list(self.input_path.iterdir())
            for study_path in study_path_list:
                if executor:
                    executor.submit(self.upload, study_path=study_path)
                else:
                    self.upload(study_path=study_path)
        else:
            if executor:
                executor.submit(self.upload, study_path=self.input_path)
            else:
                self.upload(study_path=self.input_path)
            # break

    @property
    def input_path(self):
        return self._input_path

    @input_path.setter
    def input_path(self, value: str):
        self._input_path = pathlib.Path(value)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input",
        dest="input",
        type=str,
        required=True,
        help="input rename nifti folder.\r\n",
    )
    parser.add_argument(
        "--work",
        dest="work",
        type=int,
        default=4,
        help="Process cont max values is 4 .\r\n"
        "Example: python convert_nifti.py -i input_path -o output_path --work 4",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    # input_path = pathlib.Path(r'D:\00_Chen\Task08\data\test\rename_nifti\stroke')
    upload_manager = UploadSqlManager(args.input)
    executor = ThreadPoolExecutor(max_workers=args.work)
    with executor:
        upload_manager.run()

# patient
# # study
# # # series
# # # # file
