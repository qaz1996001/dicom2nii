"""
處理策略工廠模式實作
"""
from typing import Dict, Type, List
from ..core.enums import ModalityEnum
from ..core.exceptions import ProcessingError
from .base import BaseProcessingStrategy, MRRenameSeriesProcessingStrategy

from .dicom import (
    ADCProcessingStrategy,
    ASLProcessingStrategy,
    DSCProcessingStrategy,
    DwiProcessingStrategy,
    EADCProcessingStrategy,
    ESWANProcessingStrategy,
    SWANProcessingStrategy,
    T1ProcessingStrategy,
    T2ProcessingStrategy,
    CVRProcessingStrategy,
    DTIProcessingStrategy,
    MRABrainProcessingStrategy,
    MRANeckProcessingStrategy,
    MRAVRBrainProcessingStrategy,
    MRAVRNeckProcessingStrategy,
    RestingProcessingStrategy,
)


class ProcessingStrategyFactory:
    """處理策略工廠類別"""

    # MR 處理策略註冊表 - 完整的 16 個策略
    _mr_strategy_registry: Dict[str, Type[MRRenameSeriesProcessingStrategy]] = {
        "DWI": DwiProcessingStrategy,
        "ADC": ADCProcessingStrategy,
        "eADC": EADCProcessingStrategy,
        "SWAN": SWANProcessingStrategy,
        "eSWAN": ESWANProcessingStrategy,
        "MRA_BRAIN": MRABrainProcessingStrategy,
        "MRA_NECK": MRANeckProcessingStrategy,
        "MRAVR_BRAIN": MRAVRBrainProcessingStrategy,
        "MRAVR_NECK": MRAVRNeckProcessingStrategy,
        "T1": T1ProcessingStrategy,
        "T2": T2ProcessingStrategy,
        "ASL": ASLProcessingStrategy,
        "DSC": DSCProcessingStrategy,
        "CVR": CVRProcessingStrategy,
        "RESTING": RestingProcessingStrategy,
        "DTI": DTIProcessingStrategy,
    }

    # 策略實例快取
    _strategy_cache: Dict[str, BaseProcessingStrategy] = {}

    @classmethod
    def register_strategy(
        cls, name: str, strategy_class: Type[BaseProcessingStrategy]
    ) -> None:
        """註冊新的處理策略

        Args:
            name: 策略名稱
            strategy_class: 策略類別
        """
        if not issubclass(strategy_class, BaseProcessingStrategy):
            raise ProcessingError(
                f"策略類別必須繼承自 BaseProcessingStrategy: {strategy_class}"
            )

        cls._mr_strategy_registry[name] = strategy_class

        # 清除快取中的相關項目
        if name in cls._strategy_cache:
            del cls._strategy_cache[name]

    @classmethod
    def create_strategy(cls, strategy_name: str) -> BaseProcessingStrategy:
        """建立處理策略實例

        Args:
            strategy_name: 策略名稱

        Returns:
            處理策略實例
        """
        # 檢查快取
        if strategy_name in cls._strategy_cache:
            return cls._strategy_cache[strategy_name]

        # 從註冊表中尋找策略類別
        strategy_class = cls._mr_strategy_registry.get(strategy_name)
        if not strategy_class:
            raise ProcessingError(f"未知的處理策略: {strategy_name}")

        # 建立實例並快取
        strategy_instance = strategy_class()
        cls._strategy_cache[strategy_name] = strategy_instance

        return strategy_instance

    @classmethod
    def create_all_mr_strategies(cls) -> List[MRRenameSeriesProcessingStrategy]:
        """建立所有 MR 處理策略實例

        Returns:
            所有 MR 處理策略的列表
        """
        strategies = []

        for strategy_name in cls._mr_strategy_registry.keys():
            try:
                strategy = cls.create_strategy(strategy_name)
                if isinstance(strategy, MRRenameSeriesProcessingStrategy):
                    strategies.append(strategy)
            except Exception as e:
                print(f"建立策略失敗 {strategy_name}: {str(e)}")

        return strategies

    @classmethod
    def get_strategies_for_modality(
        cls, modality: ModalityEnum
    ) -> List[BaseProcessingStrategy]:
        """根據模態獲取相應的處理策略

        Args:
            modality: 影像模態

        Returns:
            適用的處理策略列表
        """
        strategies = []

        if modality == ModalityEnum.MR:
            strategies.extend(cls.create_all_mr_strategies())
        elif modality == ModalityEnum.CT:
            # CT 策略可以在這裡添加
            pass

        return strategies

    @classmethod
    def get_available_strategies(cls) -> List[str]:
        """獲取所有可用的策略名稱

        Returns:
            策略名稱列表
        """
        return list(cls._mr_strategy_registry.keys())

    @classmethod
    def clear_cache(cls) -> None:
        """清除策略快取"""
        cls._strategy_cache.clear()


class NiftiProcessingStrategyFactory:
    """NIfTI 處理策略工廠"""

    from ..processing.nifti import (
        ADCNiftiProcessingStrategy,
        DwiNiftiProcessingStrategy,
        SWANNiftiProcessingStrategy,
        T1NiftiProcessingStrategy,
        T2NiftiProcessingStrategy,
    )

    _strategy_registry: Dict[str, type] = {
        "DWI": DwiNiftiProcessingStrategy,
        "ADC": ADCNiftiProcessingStrategy,
        "SWAN": SWANNiftiProcessingStrategy,
        "T1": T1NiftiProcessingStrategy,
        "T2": T2NiftiProcessingStrategy,
    }

    _strategy_cache: Dict[str, BaseProcessingStrategy] = {}

    @classmethod
    def create_all_strategies(cls) -> List:
        """建立所有 NIfTI 處理策略"""
        strategies = []

        for strategy_name, strategy_class in cls._strategy_registry.items():
            try:
                if strategy_name not in cls._strategy_cache:
                    cls._strategy_cache[strategy_name] = strategy_class()
                strategies.append(cls._strategy_cache[strategy_name])
            except Exception as e:
                print(f"建立 NIfTI 策略失敗 {strategy_name}: {str(e)}")

        return strategies

    @classmethod
    def create_strategy(cls, strategy_name: str):
        """建立指定的 NIfTI 處理策略"""
        if strategy_name in cls._strategy_cache:
            return cls._strategy_cache[strategy_name]

        strategy_class = cls._strategy_registry.get(strategy_name)
        if not strategy_class:
            raise ProcessingError(f"未知的 NIfTI 處理策略: {strategy_name}")

        strategy_instance = strategy_class()
        cls._strategy_cache[strategy_name] = strategy_instance

        return strategy_instance
