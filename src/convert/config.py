from enum import Enum
from typing import Union, List


class BaseEnum(Enum):
    @classmethod
    def to_list(cls) -> List[Union[Enum,]]:
        return list(map(lambda c: c, cls))


class NullEnum(BaseEnum):
    NULL = ''


class CTSeriesRenameEnum(BaseEnum):
    NCCT5mm = 'NCCT5mm'
    NCCT_COR = 'NCCT_COR'
    NCCTBONE = 'NCCTBONE'
    CECT5mm = 'CECT5mm'
    CTA = 'CTA'


class MRSeriesRenameEnum(BaseEnum):
    CVR = 'CVR'
    CVR1000 = 'CVR1000'
    CVR2000 = 'CVR2000'
    CVR2000_EAR = 'CVR2000_EAR'
    CVR2000_EYE = 'CVR2000_EYE'

    DSC_RAW = 'DSC_RAW'

    DTI32D = 'DTI32D'
    DTI64D = 'DTI64D'

    DWI = 'DWI'
    DWI0 = 'DWI0'
    DWI1000 = 'DWI1000'
    B_VALUES_1000 = '1000'
    B_VALUES_0 = '0'
    ADC = 'ADC'

    eADC = 'eADC'

    eSWAN = 'eSWAN'
    eSWANmag = 'eSWANmag'
    eSWANmIP = 'eSWANmIP'

    MRA_BRAIN = 'MRA_BRAIN'
    MRA_NECK = 'MRA_NECK'

    MRAVR_BRAIN = 'MRAVR_BRAIN'
    MRAVR_NECK = 'MRAVR_NECK'

    MRV = 'MRV'
    MRV_SAG = 'MRV_SAG'

    RESTING = 'RESTING'
    RESTING2000 = 'RESTING2000'
    SWANPHASE = 'SWANPHASE'
    SWANmIP = 'SWANmIP'
    SWAN = 'SWAN'


class SeriesEnum(BaseEnum):
    FLAIR = 'FLAIR'
    CUBE = 'CUBE'
    BRAVO = 'BRAVO'
    FSPGR = 'efgre3d'
    SWAN = 'SWAN'

    eSWAN = 'eSWAN'
    mIP = 'mIP'
    mAG = 'mAG'
    SWANPHASE = 1


class T1SeriesRenameEnum(BaseEnum):
    T1 = 'T1'
    ## 2D ##
    T1_AXI = 'T1_AXI'
    T1_COR = 'T1_COR'
    T1_SAG = 'T1_SAG'

    T1CE = 'T1CE'
    T1CE_AXI = 'T1CE_AXI'
    T1CE_COR = 'T1CE_COR'
    T1CE_SAG = 'T1CE_SAG'

    T1FLAIR = 'T1FLAIR'
    T1FLAIR_AXI = 'T1FLAIR_AXI'
    T1FLAIR_COR = 'T1FLAIR_COR'
    T1FLAIR_SAG = 'T1FLAIR_SAG'

    T1FLAIRCE = 'T1FLAIRCE'
    T1FLAIRCE_AXI = 'T1FLAIRCE_AXI'
    T1FLAIRCE_COR = 'T1FLAIRCE_COR'
    T1FLAIRCE_SAG = 'T1FLAIRCE_SAG'
    ## 2D ##

    ## 3D ORIGINAL\PRIMARY\OTHER  ##
    T1CUBE = 'T1CUBE'
    T1CUBE_AXI = 'T1CUBE_AXI'
    T1CUBE_COR = 'T1CUBE_COR'
    T1CUBE_SAG = 'T1CUBE_SAG'

    T1CUBECE = 'T1CUBECE'
    T1CUBECE_AXI = 'T1CUBECE_AXI'
    T1CUBECE_COR = 'T1CUBECE_COR'
    T1CUBECE_SAG = 'T1CUBECE_SAG'

    T1FLAIRCUBE = 'T1FLAIRCUBE'
    T1FLAIRCUBE_AXI = 'T1FLAIRCUBE_AXI'
    T1FLAIRCUBE_COR = 'T1FLAIRCUBE_COR'
    T1FLAIRCUBE_SAG = 'T1FLAIRCUBE_SAG'

    T1FLAIRCUBECE = 'T1FLAIRCUBECE'
    T1FLAIRCUBECE_AXI = 'T1FLAIRCUBECE_AXI'
    T1FLAIRCUBECE_COR = 'T1FLAIRCUBECE_COR'
    T1FLAIRCUBECE_SAG = 'T1FLAIRCUBECE_SAG'

    T1BRAVO = 'T1BRAVO'
    T1BRAVO_AXI = 'T1BRAVO_AXI'
    T1BRAVOCE_AXI = 'T1BRAVOCE_AXI'

    T1BRAVO_SAG = 'T1BRAVO_SAG'
    T1BRAVOCE_SAG = 'T1BRAVOCE_SAG'

    T1BRAVO_COR = 'T1BRAVO_COR'
    T1BRAVOCE_COR = 'T1BRAVOCE_COR'
    ## 3D ORIGINAL\PRIMARY\OTHER ##
    ## 3D REFORMATTED ##
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

    ## 3D REFORMATTED ##


class T2SeriesRenameEnum(BaseEnum):
    ## 2D ##
    T2 = 'T2'
    T2_AXI = 'T2_AXI'
    T2_COR = 'T2_COR'
    T2_SAG = 'T2_SAG'

    T2CE = 'T2CE'
    T2CE_AXI = 'T2CE_AXI'
    T2CE_COR = 'T2CE_COR'
    T2CE_SAG = 'T2CE_SAG'

    T2FLAIR = 'T2FLAIR'
    T2FLAIR_AXI = 'T2FLAIR_AXI'
    T2FLAIR_COR = 'T2FLAIR_COR'
    T2FLAIR_SAG = 'T2FLAIR_SAG'

    T2FLAIRCE = 'T2FLAIRCE'
    T2FLAIRCE_AXI = 'T2FLAIRCE_AXI'
    T2FLAIRCE_COR = 'T2FLAIRCE_COR'
    T2FLAIRCE_SAG = 'T2FLAIRCE_SAG'
    ## 2D ##
    ## 3D ORIGINAL\PRIMARY\OTHER ##
    T2CUBE = 'T2CUBE'
    T2CUBE_AXI = 'T2CUBE_AXI'
    T2CUBE_COR = 'T2CUBE_COR'
    T2CUBE_SAG = 'T2CUBE_SAG'

    T2CUBECE = 'T2CUBECE'
    T2CUBECE_AXI = 'T2CUBECE_AXI'
    T2CUBECE_COR = 'T2CUBECE_COR'
    T2CUBECE_SAG = 'T2CUBECE_SAG'

    T2FLAIRCUBE = 'T2FLAIRCUBE'
    T2FLAIRCUBE_AXI = 'T2FLAIRCUBE_AXI'
    T2FLAIRCUBE_COR = 'T2FLAIRCUBE_COR'
    T2FLAIRCUBE_SAG = 'T2FLAIRCUBE_SAG'

    T2FLAIRCUBECE = 'T2FLAIRCUBECE'
    T2FLAIRCUBECE_AXI = 'T2FLAIRCUBECE_AXI'
    T2FLAIRCUBECE_COR = 'T2FLAIRCUBECE_COR'
    T2FLAIRCUBECE_SAG = 'T2FLAIRCUBECE_SAG'
    ## 3D ORIGINAL\PRIMARY\OTHER ##
    ## 3D REFORMATTED ##

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
    ## 3D REFORMATTED ##


class ASLSEQSeriesRenameEnum(BaseEnum):
    ASLSEQ          = 'ASLSEQ'
    ASLSEQATT       = 'ASLSEQATT'
    ASLSEQATT_COLOR = 'ASLSEQATT_COLOR'

    ASLSEQCBF       = 'ASLSEQCBF'
    ASLSEQCBF_COLOR = 'ASLSEQCBF_COLOR'

    ASLPROD          = 'ASLPROD'

    ASLPRODCBF       = 'ASLPRODCBF'
    ASLPRODCBF_COLOR = 'ASLPRODCBF_COLOR'

    ASLSEQPW        = 'ASLSEQPW'
    COLOR = 'COLOR'



class DSCSeriesRenameEnum(BaseEnum):
    DSC = 'DSC'
    # DSCCBF_COLOR = 'rCBF'
    # DSCCBV_COLOR = 'rCBV'
    # DSCMTT_COLOR = 'MTT'
    rCBF = 'DSCCBF_COLOR'
    rCBV = 'DSCCBV_COLOR'
    MTT = 'DSCMTT_COLOR'


class DTISeriesEnum(BaseEnum):
    DTI32D = 32
    DTI64D = 64


class ModalityEnum(BaseEnum):
    CT = 'CT'
    MR = 'MR'


class MRAcquisitionTypeEnum(BaseEnum):
    TYPE_2D = '2D'
    TYPE_3D = '3D'


class ImageOrientationEnum(BaseEnum):
    # ORIGINAL\PRIMARY\OTHER
    SAG = 'SAG'
    AXI = 'AXI'
    COR = 'COR'
    #   r = Image Type	(DERIVED\SECONDARY\REFORMATTED\AVERAGE)
    SAGr = 'SAGr'
    AXIr = 'AXIr'
    CORr = 'CORr'


class ContrastEnum(BaseEnum):
    CE = 'CE'
    NE = 'NE'


class RepetitionTimeEnum(BaseEnum):
    TR1000 = '1000'
    TR2000 = '2000'


# (0018,0081)	Echo Time	30
class EchoTimeEnum(BaseEnum):
    TE30 = '30'


class BodyPartEnum(BaseEnum):
    EYE = 'EYE'
    EAR = 'EAR'