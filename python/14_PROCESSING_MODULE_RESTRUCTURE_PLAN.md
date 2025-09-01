# 14 - 處理模組重構計畫 (2024-01-10)

## 🎯 重構目標

根據要求，我們需要將 `processing/dicom` 和 `processing/nifti` 模組按照以下方式重新分組：

1. **structure**: T1、T2、DWI、ADC
2. **special**: MRA、SWAN、eSWAN
3. **perfusion**: DSC、ASL
4. **functional**: RESTING、CVR、DTI

同時需要嚴格遵守：
- dicom2nii-python.md 要求
- medical-reformatted-detection.md 要求
- uv-project-management.md 要求

## 📋 重構檢查清單

### 1. 分析當前模組結構
- [x] 檢查 processing/dicom 模組結構
- [x] 檢查 processing/nifti 模組結構
- [x] 識別所有處理策略類別及其功能

### 2. 設計新的模組結構
- [ ] 設計 processing/dicom 新結構
- [ ] 設計 processing/nifti 新結構
- [ ] 確保所有策略類別正確分類

### 3. 重構 processing/dicom 模組
- [ ] 建立 structure.py 模組
- [ ] 建立 special.py 模組
- [ ] 建立 perfusion.py 模組
- [ ] 建立 functional.py 模組
- [ ] 更新 __init__.py 匯入

### 4. 重構 processing/nifti 模組
- [ ] 建立 structure.py 模組
- [ ] 建立 special.py 模組
- [ ] 建立 perfusion.py 模組
- [ ] 建立 functional.py 模組
- [ ] 更新 __init__.py 匯入
- [ ] 更新 postprocess.py 引用

### 5. 測試與驗證
- [ ] 確保所有類別正確匯入
- [ ] 確保遵循 REFORMATTED 檢查規則
- [ ] 確保程式碼符合函數式程式設計風格
- [ ] 確保 RORO 模式實作

## 🔍 當前模組分析

### DICOM 處理策略 (共 16 個)

#### strategies.py 中的策略 (9個)
1. **DwiProcessingStrategy** - DWI 擴散加權影像
2. **ADCProcessingStrategy** - ADC 表觀擴散係數
3. **SWANProcessingStrategy** - SWAN 磁敏感加權影像
4. **T1ProcessingStrategy** - T1 加權影像
5. **T2ProcessingStrategy** - T2 加權影像
6. **ASLProcessingStrategy** - ASL 動脈自旋標記
7. **DSCProcessingStrategy** - DSC 動態磁敏感對比
8. **EADCProcessingStrategy** - 增強 ADC
9. **ESWANProcessingStrategy** - 增強 SWAN

#### additional_strategies.py 中的策略 (7個)
10. **MRABrainProcessingStrategy** - MRA 腦部血管
11. **MRANeckProcessingStrategy** - MRA 頸部血管
12. **MRAVRBrainProcessingStrategy** - MRA VR 腦部
13. **MRAVRNeckProcessingStrategy** - MRA VR 頸部
14. **CVRProcessingStrategy** - 腦血管反應性
15. **RestingProcessingStrategy** - 靜息態功能影像
16. **DTIProcessingStrategy** - 擴散張量影像

### NIfTI 處理策略 (共 5 個)

#### strategies.py 中的策略
1. **DwiNiftiProcessingStrategy** - DWI NIfTI 處理
2. **ADCNiftiProcessingStrategy** - ADC NIfTI 處理
3. **SWANNiftiProcessingStrategy** - SWAN NIfTI 處理
4. **T1NiftiProcessingStrategy** - T1 NIfTI 處理
5. **T2NiftiProcessingStrategy** - T2 NIfTI 處理

## 📊 新模組結構設計

### DICOM 處理策略新結構

#### 1. structure/
- **T1.py**: T1ProcessingStrategy
- **T2.py**: T2ProcessingStrategy
- **DWI.py**: DwiProcessingStrategy
- **ADC.py**: ADCProcessingStrategy, EADCProcessingStrategy

#### 2. special/
- **MRA.py**: MRABrainProcessingStrategy, MRANeckProcessingStrategy, MRAVRBrainProcessingStrategy, MRAVRNeckProcessingStrategy
- **SWAN.py**: SWANProcessingStrategy
- **eSWAN.py**: ESWANProcessingStrategy

#### 3. perfusion/
- **DSC.py**: DSCProcessingStrategy
- **ASL.py**: ASLProcessingStrategy

#### 4. functional/
- **RESTING.py**: RestingProcessingStrategy
- **CVR.py**: CVRProcessingStrategy
- **DTI.py**: DTIProcessingStrategy

### NIfTI 處理策略新結構

#### 1. structure/
- **T1.py**: T1NiftiProcessingStrategy
- **T2.py**: T2NiftiProcessingStrategy
- **DWI.py**: DwiNiftiProcessingStrategy
- **ADC.py**: ADCNiftiProcessingStrategy

#### 2. special/
- **SWAN.py**: SWANNiftiProcessingStrategy

#### 3. perfusion/
- (未來可能添加的 ASL、DSC 處理策略)

#### 4. functional/
- (未來可能添加的功能性影像處理策略)

## 🚀 實施計畫

1. 首先建立新的模組檔案結構
2. 將現有策略類別移動到相應的新模組中
3. 更新所有匯入語句
4. 更新 __init__.py 檔案以正確匯出所有類別
5. 更新 NiftiPostProcessManager 以使用新的模組結構

## 📝 注意事項

1. 確保所有 REFORMATTED 檢查邏輯保持不變
2. 保持函數式程式設計風格
3. 維護 RORO 模式的實作
4. 確保所有類別都有適當的文件字串
5. 確保所有錯誤處理符合 .cursor 規則

## 🔄 進度追蹤

### DICOM 處理策略
#### structure/
- [ ] 完成 dicom/structure/__init__.py
- [ ] 完成 dicom/structure/T1.py
- [ ] 完成 dicom/structure/T2.py
- [ ] 完成 dicom/structure/DWI.py
- [ ] 完成 dicom/structure/ADC.py

#### special/
- [ ] 完成 dicom/special/__init__.py
- [ ] 完成 dicom/special/MRA.py
- [ ] 完成 dicom/special/SWAN.py
- [ ] 完成 dicom/special/eSWAN.py

#### perfusion/
- [ ] 完成 dicom/perfusion/__init__.py
- [ ] 完成 dicom/perfusion/DSC.py
- [ ] 完成 dicom/perfusion/ASL.py

#### functional/
- [ ] 完成 dicom/functional/__init__.py
- [ ] 完成 dicom/functional/RESTING.py
- [ ] 完成 dicom/functional/CVR.py
- [ ] 完成 dicom/functional/DTI.py

- [ ] 完成 dicom/__init__.py 更新

### NIfTI 處理策略
#### structure/
- [ ] 完成 nifti/structure/__init__.py
- [ ] 完成 nifti/structure/T1.py
- [ ] 完成 nifti/structure/T2.py
- [ ] 完成 nifti/structure/DWI.py
- [ ] 完成 nifti/structure/ADC.py

#### special/
- [ ] 完成 nifti/special/__init__.py
- [ ] 完成 nifti/special/SWAN.py

- [ ] 完成 nifti/__init__.py 更新
- [ ] 完成 nifti/postprocess.py 更新
- [ ] 完成所有測試與驗證
