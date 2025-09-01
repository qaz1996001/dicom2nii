import pathlib
from concurrent.futures import ThreadPoolExecutor
from typing import Union

import requests

from . import SQL_WEB_URL


class UploadManager:
    web_url = SQL_WEB_URL

    def __init__(self, input_path: Union[str, pathlib.Path], *args, **kwargs):
        self._input_path = pathlib.Path(input_path)

    # @staticmethod
    # def get_dicom_data(dicom_ds: FileDataset):
    #     # (0010,0020)	Patient ID	05470905
    #     # (0010,0040)	Patient Sex	M
    #     # (0010,0030)	Patient Birth Date	19481009
    #     # (0008,0020)	Study Date	20220616
    #     # (0008,0050)	Accession Number	21106150005
    #     patients_id = dicom_ds[0x10, 0x20].value
    #     gender = dicom_ds[0x10, 0x40].value
    #     birth_date = dicom_ds[0x10, 0x30].value
    #     studies_date = dicom_ds[0x08, 0x20].value
    #     studies_time = dicom_ds[0x08, 0x30].value
    #     studies_description = dicom_ds[0x08, 0x1030].value
    #     accession_number = dicom_ds[0x08, 0x50].value
    #     # (0008,0021)	Series Date	20220616
    #     series_date = dicom_ds[0x08, 0x21].value
    #     series_time = dicom_ds[0x08, 0x31].value
    #     if '.' in studies_time:
    #         studies_time = studies_time.split('.')[0]
    #     if '.' in series_time:
    #         series_time = series_time.split('.')[0]
    #
    #     modality = dicom_ds[0x08, 0x60].value
    #     return dict(patients_id=patients_id, gender=gender, birth_date=birth_date,
    #                 studies_date=studies_date, studies_time=studies_time,
    #                 studies_description=studies_description, accession_number=accession_number,
    #                 series_date=series_date, series_time=series_time, modality=modality)
    #
    #
    #
    # def upload_patient_study(self, study_path: pathlib.Path):
    #     json_file_path = list(study_path.joinpath('.meta').iterdir())[-1]
    #     print('json_file_path',json_file_path)
    #     with open(f'{json_file_path}', encoding='utf8') as file:
    #         orjson_dict = orjson.loads(file.read())
    #     print(orjson_dict.keys())
    #     with requests.Session() as session:
    #         for key, value in orjson_dict.items():
    #             dicom_ds = Dataset.from_json(value[0])
    #             dicom_data = self.get_dicom_data(dicom_ds=dicom_ds)
    #             dicom_data['series_description'] = json_file_path.name.replace('.jsonlines','')
    #             json_data = {"data_list": [dicom_data]}
    #             response = session.post(url=f'{self.web_url}series/', json=json_data)
    #     print(response)
    #
    #
    # def upload_series(self, study_path: pathlib.Path):
    #     json_file_path_list = list(study_path.joinpath('.meta').iterdir())
    #     data_list =[]
    #     for json_file_path in json_file_path_list:
    #         with open(f'{json_file_path}', encoding='utf8') as file:
    #             orjson_dict = orjson.loads(file.read())
    #             for key, value in orjson_dict.items():
    #                 dicom_ds = Dataset.from_json(value[0])
    #                 dicom_data = self.get_dicom_data(dicom_ds=dicom_ds)
    #                 dicom_data['series_description'] = json_file_path.name.replace('.jsonlines','')
    #                 data_list.append(dicom_data)
    #     json_data = {"data_list": data_list}
    #     with requests.Session() as session:
    #         response = session.post(url=f'{self.web_url}series/', json=json_data)
    #         print(response)
    #
    # def upload_sql(self, study_path: pathlib.Path):
    #     self.upload_patient_study(study_path=study_path)
    #     self.upload_series(study_path=study_path)

    def upload_file_meta_data_to_sql(
        self, study_path: pathlib.Path, path: pathlib.Path, is_niigz_meta=True
    ):
        if is_niigz_meta:
            Key = f"{study_path.name}/{path.parent.name}/{path.name}"
        else:
            Key = f"{study_path.name}/{path.name}"
        files = {"file": open(path, "rb")}
        form_data = {"file_url": Key}
        print("file_url", Key)
        # form_data = dict(file_name= path.name,
        #                  file_size= object.get('ContentLength'),
        #                  file_datetime= object.get('LastModified'),
        #                  file_type= path.suffix,
        #                  file_url= Key,)
        with requests.Session() as session:
            response = session.post(
                url=f"{self.web_url}file/", files=files, data=form_data
            )
            print(response)

    def upload(self, study_path):
        # info_pattern = re.compile('(\d{8})_(\d{8})_(MR|CT)_(\w*)')
        # print(info_pattern.match(study_path.name).groups())
        for series_path in study_path.iterdir():
            if series_path.is_dir():
                for path in series_path.iterdir():
                    self.upload_file_meta_data_to_sql(study_path=study_path, path=path)
            if series_path.is_file():
                self.upload_file_meta_data_to_sql(
                    study_path=study_path, path=series_path, is_niigz_meta=False
                )

    def run(self, executor: Union[ThreadPoolExecutor, None] = None):
        is_dir_flag = all(x.is_dir() for x in self.input_path.iterdir())
        if is_dir_flag:
            study_path_list = list(self.input_path.iterdir())
            for study_path in study_path_list:
                if executor:
                    executor.submit(self.upload, study_path=study_path)
                else:
                    self.upload(study_path=study_path)
                # break
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
