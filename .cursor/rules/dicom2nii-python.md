# 醫學影像 DICOM2NII 專案重構提示詞

我需要重構一個醫學影像處理專案，包含 DICOM 到 NIfTI 轉換功能。

## 專案背景
- **領域**: 醫學影像處理 (MRI, CT)
- **主要功能**: DICOM 重新命名、NIfTI 轉換、後處理、上傳
- **關鍵要求**: 支援 REFORMATTED 影像檢查、T1/T2 完整序列支援

## 技術要求 (MANDATORY)
1. **專案管理**: 必須使用 uv (不使用 pip)
2. **Python 風格**: 嚴格遵循函數式程式設計
3. **RORO 模式**: 所有處理函數使用 Receive Object, Return Object
4. **醫學準確性**: DICOM 標籤處理必須保持醫學準確性
5. **REFORMATTED 檢查**: 必須檢查 (0008,0008) Image Type

## 處理策略要求
需要實作 16 個完整的醫學影像處理策略：
- 基礎策略 (7個): DWI, ADC, SWAN, T1, T2, ASL, DSC
- 增強策略 (2個): eADC, eSWAN  
- MRA 策略 (4個): MRA_BRAIN, MRA_NECK, MRAVR_BRAIN, MRAVR_NECK
- 功能性策略 (3個): CVR, RESTING, DTI

## T1/T2 序列要求
- **T1**: 32 種組合 (包含所有 REFORMATTED 變體)
- **T2**: 24 種組合 (包含所有 REFORMATTED 變體)
- **REFORMATTED 支援**: T1CUBE_AXIr, T2CUBECE_AXIr 等

## 請在開始前：
1. 建立完整的 .cursor/rules 配置 (醫學影像專用)
2. 設定 uv 專案管理 (pyproject.toml)
3. 建立詳細的實作計畫 (有序號的 .md 檔案)
4. 分析現有程式碼的醫學邏輯正確性
5. 確保所有 DICOM 處理符合醫學標準

請嚴格遵循醫學影像處理的專業要求，確保病人安全和資料準確性。

### 5. **完整的 context 配置**

```json
{
  "medical_imaging_context": {
    "domain": "medical_imaging",
    "modalities": ["MRI", "CT"],
    "sequence_types": ["T1", "T2", "DWI", "ADC", "SWAN", "ASL", "DSC", "MRA", "CVR", "DTI"],
    "reformatted_support": true,
    "dicom_tags_critical": [
      "(0008,0008) Image Type",
      "(0008,103E) Series Description", 
      "(0018,0023) MR Acquisition Type",
      "(0020,0037) Image Orientation"
    ],
    "processing_strategies_count": 16,
    "quality_requirements": {
      "type_hints_coverage": "100%",
      "functional_programming": "mandatory",
      "roro_pattern": "mandatory",
      "early_return": "mandatory"
    }
  },
  "project_management": {
    "package_manager": "uv_only",
    "config_file": "pyproject.toml",
    "python_version": ">=3.9",
    "development_tools": ["black", "ruff", "mypy", "pytest"]
  },
  "documentation_structure": {
    "numbered_files": true,
    "reading_order": "sequential",
    "medical_accuracy_notes": "mandatory"
  }
}
```
