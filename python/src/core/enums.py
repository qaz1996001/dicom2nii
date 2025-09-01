"""
所有枚舉類別的統一定義
"""

from enum import Enum
from typing import Union


class BaseEnum(Enum):
    """基礎枚舉類別，提供通用方法"""

    @classmethod
    def to_list(cls) -> list[Union[Enum,]]:
        """將枚舉轉換為列表"""
        return list(cls)


class NullEnum(BaseEnum):
    """空值枚舉"""
    NULL = ''


class ModalityEnum(BaseEnum):
    """影像模態枚舉"""
    CT = 'CT'
    MR = 'MR'


class MRAcquisitionTypeEnum(BaseEnum):
    """MR 獲取類型枚舉"""
    TYPE_2D = '2D'
    TYPE_3D = '3D'


class ImageOrientationEnum(BaseEnum):
    """影像方向枚舉"""
    # ORIGINAL\PRIMARY\OTHER
    SAG = 'SAG'  # 矢狀面
    AXI = 'AXI'  # 軸狀面
    COR = 'COR'  # 冠狀面
    # r = Image Type (DERIVED\SECONDARY\REFORMATTED\AVERAGE)
    SAGr = 'SAGr'
    AXIr = 'AXIr'
    CORr = 'CORr'


class ContrastEnum(BaseEnum):
    """對比劑枚舉"""
    CE = 'CE'  # Contrast Enhanced
    NE = 'NE'  # Non-Enhanced


class RepetitionTimeEnum(BaseEnum):
    """重複時間枚舉"""
    TR1000 = '1000'
    TR2000 = '2000'


class EchoTimeEnum(BaseEnum):
    """回音時間枚舉"""
    TE30 = '30'


class BodyPartEnum(BaseEnum):
    """身體部位枚舉"""
    EYE = 'EYE'
    EAR = 'EAR'


class SeriesEnum(BaseEnum):
    """序列類型枚舉"""
    FLAIR = 'FLAIR'
    CUBE = 'CUBE'
    BRAVO = 'BRAVO'
    FSPGR = 'efgre3d'
    SWAN = 'SWAN'
    eSWAN = 'eSWAN'
    mIP = 'mIP'
    mAG = 'mAG'
    ORIGINAL = 'ORIGINAL'
    SWANPHASE = 1


class CTSeriesRenameEnum(BaseEnum):
    """CT 序列重新命名枚舉"""
    NCCT5mm = 'NCCT5mm'
    NCCT_COR = 'NCCT_COR'
    NCCTBONE = 'NCCTBONE'
    CECT5mm = 'CECT5mm'
    CTA = 'CTA'


class MRSeriesRenameEnum(BaseEnum):
    """MR 序列重新命名枚舉"""
    # CVR 相關
    CVR = 'CVR'
    CVR1000 = 'CVR1000'
    CVR2000 = 'CVR2000'
    CVR2000_EAR = 'CVR2000_EAR'
    CVR2000_EYE = 'CVR2000_EYE'

    # Resting 相關
    RESTING = 'RESTING'
    RESTING2000 = 'RESTING2000'

    # DSC 相關
    DSC_RAW = 'DSC_RAW'

    # DTI 相關
    DTI32D = 'DTI32D'
    DTI64D = 'DTI64D'

    # DWI 相關
    ADC = 'ADC'
    DWI = 'DWI'
    DWI0 = 'DWI0'
    DWI1000 = 'DWI1000'
    B_VALUES_1000 = '1000'
    B_VALUES_0 = '0'

    # SWAN 相關
    SWAN = 'SWAN'
    SWANmIP = 'SWANmIP'
    SWANPHASE = 'SWANPHASE'

    # eSWAN 相關
    eADC = 'eADC'
    eSWAN = 'eSWAN'
    eSWANmag = 'eSWANmag'
    eSWANmIP = 'eSWANmIP'

    # MRA 相關
    MRA_BRAIN = 'MRA_BRAIN'
    MRA_NECK = 'MRA_NECK'
    MRAVR_BRAIN = 'MRAVR_BRAIN'
    MRAVR_NECK = 'MRAVR_NECK'

    # MRV 相關
    MRV = 'MRV'
    MRV_SAG = 'MRV_SAG'


class T1SeriesRenameEnum(BaseEnum):
    """T1 序列重新命名枚舉"""
    T1 = 'T1'

    # 2D T1
    T1_AXI = 'T1_AXI'
    T1_COR = 'T1_COR'
    T1_SAG = 'T1_SAG'

    # T1 對比劑增強
    T1CE = 'T1CE'
    T1CE_AXI = 'T1CE_AXI'
    T1CE_COR = 'T1CE_COR'
    T1CE_SAG = 'T1CE_SAG'

    # T1 FLAIR
    T1FLAIR = 'T1FLAIR'
    T1FLAIR_AXI = 'T1FLAIR_AXI'
    T1FLAIR_COR = 'T1FLAIR_COR'
    T1FLAIR_SAG = 'T1FLAIR_SAG'

    # T1 FLAIR 對比劑增強
    T1FLAIRCE = 'T1FLAIRCE'
    T1FLAIRCE_AXI = 'T1FLAIRCE_AXI'
    T1FLAIRCE_COR = 'T1FLAIRCE_COR'
    T1FLAIRCE_SAG = 'T1FLAIRCE_SAG'

    # 3D T1 CUBE
    T1CUBE = 'T1CUBE'
    T1CUBE_AXI = 'T1CUBE_AXI'
    T1CUBE_COR = 'T1CUBE_COR'
    T1CUBE_SAG = 'T1CUBE_SAG'

    # 3D T1 CUBE 對比劑增強
    T1CUBECE = 'T1CUBECE'
    T1CUBECE_AXI = 'T1CUBECE_AXI'
    T1CUBECE_COR = 'T1CUBECE_COR'
    T1CUBECE_SAG = 'T1CUBECE_SAG'

    # 3D T1 FLAIR CUBE
    T1FLAIRCUBE = 'T1FLAIRCUBE'
    T1FLAIRCUBE_AXI = 'T1FLAIRCUBE_AXI'
    T1FLAIRCUBE_COR = 'T1FLAIRCUBE_COR'
    T1FLAIRCUBE_SAG = 'T1FLAIRCUBE_SAG'

    # 3D T1 FLAIR CUBE 對比劑增強
    T1FLAIRCUBECE = 'T1FLAIRCUBECE'
    T1FLAIRCUBECE_AXI = 'T1FLAIRCUBECE_AXI'
    T1FLAIRCUBECE_COR = 'T1FLAIRCUBECE_COR'
    T1FLAIRCUBECE_SAG = 'T1FLAIRCUBECE_SAG'

    # T1 BRAVO
    T1BRAVO = 'T1BRAVO'
    T1BRAVO_AXI = 'T1BRAVO_AXI'
    T1BRAVOCE_AXI = 'T1BRAVOCE_AXI'
    T1BRAVO_SAG = 'T1BRAVO_SAG'
    T1BRAVOCE_SAG = 'T1BRAVOCE_SAG'
    T1BRAVO_COR = 'T1BRAVO_COR'
    T1BRAVOCE_COR = 'T1BRAVOCE_COR'

    # 3D REFORMATTED
    T1CUBE_AXIr = 'T1CUBE_AXIr'
    T1CUBE_CORr = 'T1CUBE_CORr'
    T1CUBE_SAGr = 'T1CUBE_SAGr'
    T1CUBECE_AXIr = 'T1CUBECE_AXIr'
    T1CUBECE_CORr = 'T1CUBECE_CORr'
    T1CUBECE_SAGr = 'T1CUBECE_SAGr'
    T1FLAIRCUBE_AXIr = 'T1FLAIRCUBE_AXIr'
    T1FLAIRCUBE_CORr = 'T1FLAIRCUBE_CORr'
    T1FLAIRCUBE_SAGr = 'T1FLAIRCUBE_SAGr'
    T1FLAIRCUBECE_AXIr = 'T1FLAIRCUBECE_AXIr'
    T1FLAIRCUBECE_CORr = 'T1FLAIRCUBECE_CORr'
    T1FLAIRCUBECE_SAGr = 'T1FLAIRCUBECE_SAGr'
    T1BRAVO_AXIr = 'T1BRAVO_AXIr'
    T1BRAVOCE_AXIr = 'T1BRAVOCE_AXIr'
    T1BRAVO_SAGr = 'T1BRAVO_SAGr'
    T1BRAVOCE_SAGr = 'T1BRAVOCE_SAGr'
    T1BRAVO_CORr = 'T1BRAVO_CORr'
    T1BRAVOCE_CORr = 'T1BRAVOCE_CORr'


class T2SeriesRenameEnum(BaseEnum):
    """T2 序列重新命名枚舉"""
    T2 = 'T2'

    # 2D T2
    T2_AXI = 'T2_AXI'
    T2_COR = 'T2_COR'
    T2_SAG = 'T2_SAG'

    # T2 對比劑增強
    T2CE = 'T2CE'
    T2CE_AXI = 'T2CE_AXI'
    T2CE_COR = 'T2CE_COR'
    T2CE_SAG = 'T2CE_SAG'

    # T2 FLAIR
    T2FLAIR = 'T2FLAIR'
    T2FLAIR_AXI = 'T2FLAIR_AXI'
    T2FLAIR_COR = 'T2FLAIR_COR'
    T2FLAIR_SAG = 'T2FLAIR_SAG'

    # T2 FLAIR 對比劑增強
    T2FLAIRCE = 'T2FLAIRCE'
    T2FLAIRCE_AXI = 'T2FLAIRCE_AXI'
    T2FLAIRCE_COR = 'T2FLAIRCE_COR'
    T2FLAIRCE_SAG = 'T2FLAIRCE_SAG'

    # 3D T2 CUBE
    T2CUBE = 'T2CUBE'
    T2CUBE_AXI = 'T2CUBE_AXI'
    T2CUBE_COR = 'T2CUBE_COR'
    T2CUBE_SAG = 'T2CUBE_SAG'

    # 3D T2 CUBE 對比劑增強
    T2CUBECE = 'T2CUBECE'
    T2CUBECE_AXI = 'T2CUBECE_AXI'
    T2CUBECE_COR = 'T2CUBECE_COR'
    T2CUBECE_SAG = 'T2CUBECE_SAG'

    # 3D T2 FLAIR CUBE
    T2FLAIRCUBE = 'T2FLAIRCUBE'
    T2FLAIRCUBE_AXI = 'T2FLAIRCUBE_AXI'
    T2FLAIRCUBE_COR = 'T2FLAIRCUBE_COR'
    T2FLAIRCUBE_SAG = 'T2FLAIRCUBE_SAG'

    # 3D T2 FLAIR CUBE 對比劑增強
    T2FLAIRCUBECE = 'T2FLAIRCUBECE'
    T2FLAIRCUBECE_AXI = 'T2FLAIRCUBECE_AXI'
    T2FLAIRCUBECE_COR = 'T2FLAIRCUBECE_COR'
    T2FLAIRCUBECE_SAG = 'T2FLAIRCUBECE_SAG'

    # 3D REFORMATTED
    T2CUBE_AXIr = 'T2CUBE_AXIr'
    T2CUBE_CORr = 'T2CUBE_CORr'
    T2CUBE_SAGr = 'T2CUBE_SAGr'
    T2CUBECE_AXIr = 'T2CUBECE_AXIr'
    T2CUBECE_CORr = 'T2CUBECE_CORr'
    T2CUBECE_SAGr = 'T2CUBECE_SAGr'
    T2FLAIRCUBE_AXIr = 'T2FLAIRCUBE_AXIr'
    T2FLAIRCUBE_CORr = 'T2FLAIRCUBE_CORr'
    T2FLAIRCUBE_SAGr = 'T2FLAIRCUBE_SAGr'
    T2FLAIRCUBECE_AXIr = 'T2FLAIRCUBECE_AXIr'
    T2FLAIRCUBECE_SAGr = 'T2FLAIRCUBECE_SAGr'
    T2FLAIRCUBECE_CORr = 'T2FLAIRCUBECE_CORr'


class ASLSEQSeriesRenameEnum(BaseEnum):
    """ASL 序列重新命名枚舉"""
    ASLSEQ = 'ASLSEQ'
    ASLSEQATT = 'ASLSEQATT'
    ASLSEQATT_COLOR = 'ASLSEQATT_COLOR'
    ASLSEQCBF = 'ASLSEQCBF'
    ASLSEQCBF_COLOR = 'ASLSEQCBF_COLOR'
    ASLPROD = 'ASLPROD'
    ASLPRODCBF = 'ASLPRODCBF'
    ASLPRODCBF_COLOR = 'ASLPRODCBF_COLOR'
    ASLSEQPW = 'ASLSEQPW'
    ASL = 'ASL'
    CBF = 'CBF'
    COLOR = 'COLOR'
    Cerebral_Blood_Flow = 'Cerebral Blood Flow'


class DSCSeriesRenameEnum(BaseEnum):
    """DSC 序列重新命名枚舉"""
    DSC = 'DSC'
    rCBF = 'DSCCBF_COLOR'
    rCBV = 'DSCCBV_COLOR'
    MTT = 'DSCMTT_COLOR'


class DTISeriesEnum(BaseEnum):
    """DTI 序列枚舉"""
    DTI32D = 32
    DTI64D = 64
