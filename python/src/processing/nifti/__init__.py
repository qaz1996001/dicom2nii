"""
NIfTI 處理策略模組
"""

from src.processing.nifti.postprocess import NiftiPostProcessManager
from src.processing.nifti.special import SWANNiftiProcessingStrategy
from src.processing.nifti.structure import (
    ADCNiftiProcessingStrategy,
    DwiNiftiProcessingStrategy,
    T1NiftiProcessingStrategy,
    T2NiftiProcessingStrategy,
)

__all__ = [
    # Structure
    "T1NiftiProcessingStrategy",
    "T2NiftiProcessingStrategy",
    "DwiNiftiProcessingStrategy",
    "ADCNiftiProcessingStrategy",
    # Special
    "SWANNiftiProcessingStrategy",
    # Manager
    "NiftiPostProcessManager",
]
