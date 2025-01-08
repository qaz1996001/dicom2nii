import argparse
import enum
import pathlib
import re

import numpy as np
import pandas as  pd

from convert.config import T1SeriesRenameEnum,MRSeriesRenameEnum, T2SeriesRenameEnum
import orjson

class InferenceEnum(str,enum.Enum):
    CMB = 'CMB'
    DWI = 'DWI'
    WMH_PVS = 'WMH_PVS'
    Area = 'Area'
    Infarct= 'Infarct'
    WMH = 'WMH'
    Aneurysm = 'Aneurysm'
    AneurysmSynthSeg = 'AneurysmSynthSeg'
    # Lacune

model_mapping_series_dict = {InferenceEnum.Area:[#{T1SeriesRenameEnum.T1BRAVO_AXI,},
                                                 #{T1SeriesRenameEnum.T1BRAVO_SAG,},
                                                 # {T1SeriesRenameEnum.T1BRAVO_COR,},
                                                 # {T1SeriesRenameEnum.T1FLAIR_AXI,},
                                                 # {T1SeriesRenameEnum.T1FLAIR_SAG,},
                                                 #{T1SeriesRenameEnum.T1FLAIR_COR,}
                                                 [T1SeriesRenameEnum.T1BRAVO_AXI,],
                                                 [T1SeriesRenameEnum.T1BRAVO_SAG,],
                                                 [T1SeriesRenameEnum.T1BRAVO_COR,],
                                                 [T1SeriesRenameEnum.T1FLAIR_AXI,],
                                                 [T1SeriesRenameEnum.T1FLAIR_SAG,],
                                                 [T1SeriesRenameEnum.T1FLAIR_COR,],
                                                 ],
                             InferenceEnum.DWI:[ #[MRSeriesRenameEnum.DWI0, T1SeriesRenameEnum.T1BRAVO_AXI,],
                                                 # [MRSeriesRenameEnum.DWI0, T1SeriesRenameEnum.T1FLAIR_AXI,],
                                                   [MRSeriesRenameEnum.DWI0]


                                                 ],
                             InferenceEnum.WMH_PVS:[[T2SeriesRenameEnum.T2FLAIR_AXI,]],
                             InferenceEnum.CMB:[[MRSeriesRenameEnum.SWAN,T1SeriesRenameEnum.T1BRAVO_AXI],
                                                #Ax SWAN_resample_synthseg33_from_Sag_FSPGR_BRAVO_resample_synthseg33.nii.gz
                                                [MRSeriesRenameEnum.SWAN,T1SeriesRenameEnum.T1FLAIR_AXI],
                                                ],
                             InferenceEnum.AneurysmSynthSeg: [[MRSeriesRenameEnum.MRA_BRAIN]],
                             InferenceEnum.Infarct:[[MRSeriesRenameEnum.DWI0,
                                                     MRSeriesRenameEnum.DWI1000,
                                                     MRSeriesRenameEnum.ADC],],
                             InferenceEnum.WMH :[[T2SeriesRenameEnum.T2FLAIR_AXI,]],

                             InferenceEnum.Aneurysm: [[MRSeriesRenameEnum.MRA_BRAIN]]
}

# C:\Users\tmu3090\Desktop\Task\dicom2nii\src\mapping.json
# E:\PC_3090\data\output\PSCL_MRI\08292236_20160707_MR_E42557741501
# "E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\synthseg_DWI0_original_DWI.json",
# intput
# Infarct":["E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\ADC.nii.gz",
# "E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\DWI0.nii.gz",
# "E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\DWI1000.nii.gz",
# "E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\synthseg_DWI0_original_DWI.nii.gz",
# ]
# "WMH": ["E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\T2FLAIR_AXI.nii.gz",
#         "E:\\PC_3090\\data\\rename_nifti\\PSCL_MRI\\00003092_20201007_MR_20910070157\\synthseg_T2FLAIR_AXI_original_WMHPVS.nii.gz",
# ],
# output
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Infarct.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Infarct_ADCth.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Infarct_synthseg.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Infarct.json
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_WMH.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_WMH_synthseg.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_WMH.json
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Aneurysm.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Prob_Aneurysm.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Vessel.nii.gz
# output_path /mnt/e/PC_3090/data/output/PSCL_MRI/00003092_20201007_MR_20910070157/Pred_Aneurysm.json


study_id_pattern = re.compile('^[0-9]{8}_[0-9]{8}_(MR|CT|CR|PR).*$', re.IGNORECASE)
# 00003092_20201007_MR_20910070157
def check_study_id(intput_path :pathlib.Path)->bool:
    global study_id_pattern
    if intput_path.is_dir():
        result = study_id_pattern.match(intput_path.name)
        if result is not None:
            return True
    return False

def check_study_mapping_inference(study_path:pathlib.Path):
    file_list = sorted(study_path.iterdir())
    if any(filter(lambda x: x.name.endswith('nii.gz') or x.name.endswith('nii') , file_list)):
        df_file = pd.DataFrame(file_list,columns=['file_path'])
        df_file['file_name'] = df_file['file_path'].map(lambda x: x.name.replace('.nii.gz', ''))
        model_mapping_dict = {}
        for model_name, model_mapping_series_list in model_mapping_series_dict.items():
            for mapping_series in model_mapping_series_list:
                mapping_series_str = list(map(lambda x:x.value,mapping_series))
                result = np.intersect1d(df_file['file_name'], mapping_series_str,return_indices=True)

                if result[0].shape[0] >= len(mapping_series_str):
                    df_result = df_file.iloc()[result[1]]
                    file_path = list(map(lambda x:str(x),df_result['file_path'].to_list()))
                    model_mapping_dict.update({model_name.value:file_path})
                    break
        return {study_path.name:model_mapping_dict}



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dicom', dest='input_dicom', type=str,
                        help="input the raw dicom folder.\r\n")
    parser.add_argument('--work', dest='work', type=int, default=4,
                        help="Thread cont .\r\n"
                             "Example ： "
                             "--output_nifti output_nifti_path --work 4")

    return parser.parse_args()
def main(args):
    pass


if __name__ == '__main__':
    input_dir = pathlib.Path(r'E:\PC_3090\data\rename_nifti\PSCL_MRI')
    input_dir_list = sorted(input_dir.iterdir())
    study_list = list(filter(check_study_id,input_dir_list))
    mapping_inference_list = list(map(check_study_mapping_inference, study_list))
    with open('mapping.json',mode='wb+') as f:
        f.write(orjson.dumps(mapping_inference_list))

