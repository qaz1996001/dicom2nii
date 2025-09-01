# DICOM2NII Python 專案重構計畫

## 專案概述
這是一個用於處理醫學影像的 DICOM 到 NIfTI 轉換工具，包含重新命名、轉換、後處理和上傳功能。

## 當前程式碼結構分析

### 主要模組結構

#### 1. `src/main.py` - 主要入口點
**功能**: 
- 命令列參數解析
- 協調各個處理步驟的執行
- 管理多執行緒處理

**問題**:
- 函數過於龐大，缺乏適當的分離
- 硬編碼的匯入語句
- 缺乏錯誤處理

#### 2. `src/convert/` - 轉換模組

##### 2.1 `base.py` - 基礎類別
**功能**:
- `ProcessingStrategy`: 抽象處理策略基類
- `SeriesProcessingStrategy`: 序列處理策略基類
- `ModalityProcessingStrategy`: 模態處理策略
- `ImageOrientationProcessingStrategy`: 影像方向處理策略
- `ContrastProcessingStrategy`: 對比劑處理策略
- `MRAcquisitionTypeProcessingStrategy`: MR 獲取類型處理策略
- `MRRenameSeriesProcessingStrategy`: MR 重新命名序列處理策略
- `CTRenameSeriesProcessingStrategy`: CT 重新命名序列處理策略

**問題**:
- 類別職責不夠明確
- 缺乏統一的錯誤處理機制

##### 2.2 `config.py` - 配置檔案
**功能**:
- 定義各種枚舉類型
- SQL 連線 URL 配置

**問題**:
- 配置散落在不同地方
- 缺乏環境變數支援

##### 2.3 `dicom_rename_mr.py` - MR DICOM 重新命名
**功能**:
- 實現各種 MR 影像類型的處理策略
- `ConvertManager`: 管理整個轉換流程

**問題**:
- 檔案過大 (1900+ 行)
- 重複的程式碼模式
- 策略類別結構相似但實作分散

##### 2.4 `convert_nifti.py` - DICOM 到 NIfTI 轉換
**功能**:
- `Dicm2NiixConverter`: 執行 dcm2niix 轉換

**問題**:
- 硬編碼的排除集合
- 缺乏配置彈性

##### 2.5 `convert_nifti_postprocess.py` - NIfTI 後處理
**功能**:
- 各種 NIfTI 檔案的後處理策略
- `PostProcessManager`: 管理後處理流程

**問題**:
- 與 dicom_rename_mr_postprocess.py 功能重複
- 處理邏輯相似但分散

##### 2.6 `dicom_rename_mr_postprocess.py` - DICOM 後處理
**功能**:
- DICOM 檔案的後處理
- 元資料生成

**問題**:
- 與其他後處理模組功能重疊
- 硬編碼的排除標籤

##### 2.7 `convert_nifti_to_dicom.py` - NIfTI 到 DICOM 轉換
**功能**:
- `Nifti2DicmConverter`: 反向轉換功能

##### 2.8 `list_dicom.py` 和 `list_nii.py` - 檔案列表功能
**功能**:
- 生成 DICOM 和 NIfTI 檔案的統計報告

**問題**:
- 功能重複，可以合併

#### 3. `src/upload/` - 上傳模組

##### 3.1 `upload_nifti.py` - NIfTI 上傳
**功能**:
- `UploadManager`: 上傳 NIfTI 檔案到伺服器

**問題**:
- 大量註解掉的程式碼
- 缺乏適當的錯誤處理

##### 3.2 `update_sql.py` - SQL 更新
**功能**:
- `UploadSqlManager`: 管理 SQL 資料庫更新

**問題**:
- 功能不完整，多數方法為空

## 重構目標

### 1. 架構重新設計
- 實施清晰的分層架構
- 分離關注點
- 提高可測試性和可維護性

### 2. 程式碼品質改善
- 消除重複程式碼
- 統一命名慣例
- 添加完整的型別提示
- 改善錯誤處理

### 3. 模組化改善
- 重新組織模組結構
- 建立清晰的依賴關係
- 提高程式碼重用性

## 重構計畫

### 階段 1: 基礎架構重構
1. **重構基礎類別系統**
   - 統一 `ProcessingStrategy` 介面
   - 建立清晰的抽象層次
   - 實施統一的錯誤處理

2. **重構配置管理**
   - 集中化配置管理
   - 支援環境變數
   - 分離不同類型的配置

### 階段 2: 核心功能重構
3. **重構處理策略**
   - 合併相似的策略類別
   - 消除重複程式碼
   - 實施工廠模式

4. **重構轉換器**
   - 統一轉換器介面
   - 改善錯誤處理
   - 添加進度追蹤

5. **重構管理器類別**
   - 簡化管理器邏輯
   - 統一執行流程
   - 改善並行處理

### 階段 3: 介面和整合
6. **重構主要入口點**
   - 簡化 main.py
   - 實施命令模式
   - 改善參數驗證

7. **完善型別提示和文件**
   - 添加完整的型別提示
   - 撰寫詳細的文件字串
   - 建立使用範例

## 識別的重複和多餘程式碼

### 1. 重複的處理策略模式 ⚠️ 高優先級
- **3個不同的 `ProcessingStrategy` 基類**: 
  - `base.py` 中的 `ProcessingStrategy`
  - `convert_nifti_postprocess.py` 中的 `ProcessingStrategy`
  - `dicom_rename_mr_postprocess.py` 中的 `ProcessingStrategy`
- **重複的策略實作模式**: 所有策略類別都有相似的結構和方法
- **`dicom_rename_mr.py` 中 15+ 個策略類別**: 大量重複的程式碼模式

### 2. 重複的管理器模式 ⚠️ 高優先級
- **3個 `PostProcessManager` 類別**: 
  - `convert_nifti_postprocess.py`
  - `dicom_rename_mr_postprocess.py`
  - 功能重疊但實作分散
- **2個 `ConvertManager` 類別**:
  - `dicom_rename_mr.py`
  - `dicom_rename.py` (可能是舊版本)
- **相似的 `run()` 方法**: 7個檔案中有幾乎相同的 `run()` 方法實作

### 3. 重複的檔案操作 🔄 中優先級
- **檔案重新命名邏輯**: `rename_file_suffix()` 和 `rename_file_only()` 在多個類別中重複
- **檔案大小檢查**: `del_file()` 方法在多個策略中重複
- **路徑處理**: `input_path` 和 `output_path` 的 property 設定重複

### 4. 重複的參數解析 🔄 中優先級
- **7個檔案中有 `parse_arguments()` 函數**: 大部分參數和結構相似
- **相似的命令列介面**: 重複的參數定義和說明文字

### 5. 重複的匯入和依賴 🔄 中優先級
- **相同的匯入語句**: 多個檔案匯入相同的模組
- **硬編碼的路徑操作**: `pathlib.Path` 的使用模式重複

### 6. 未使用的程式碼 🗑️ 低優先級
- **大量註解掉的程式碼**: 特別是在 `upload_nifti.py` 中
- **空的方法實作**: `update_sql.py` 中多個未實作的方法
- **測試檔案**: `convert_test.py` 可能不再需要

## 新架構設計

### 核心模組
```
src/
├── core/                    # 核心功能
│   ├── __init__.py
│   ├── config.py           # 統一配置管理
│   ├── enums.py            # 所有枚舉定義
│   ├── exceptions.py       # 自定義例外
│   └── types.py            # 型別定義
├── processing/             # 處理策略
│   ├── __init__.py
│   ├── base.py            # 基礎處理策略
│   ├── dicom/             # DICOM 處理
│   │   ├── __init__.py
│   │   ├── strategies.py  # DICOM 處理策略
│   │   └── postprocess.py # DICOM 後處理
│   └── nifti/             # NIfTI 處理
│       ├── __init__.py
│       ├── strategies.py  # NIfTI 處理策略
│       └── postprocess.py # NIfTI 後處理
├── converters/             # 轉換器
│   ├── __init__.py
│   ├── base.py            # 基礎轉換器
│   ├── dicom_to_nifti.py  # DICOM 到 NIfTI
│   └── nifti_to_dicom.py  # NIfTI 到 DICOM
├── managers/               # 管理器
│   ├── __init__.py
│   ├── base.py            # 基礎管理器
│   ├── convert_manager.py # 轉換管理器
│   └── upload_manager.py  # 上傳管理器
├── utils/                  # 工具函數
│   ├── __init__.py
│   ├── file_operations.py # 檔案操作
│   ├── dicom_utils.py     # DICOM 工具
│   └── reporting.py       # 報告生成
└── cli/                    # 命令列介面
    ├── __init__.py
    ├── commands.py        # 命令定義
    └── main.py            # 主要入口點
```

## 重構檢查清單

### ✅ 已完成項目
- [x] 程式碼結構分析
- [x] 功能清單建立
- [x] 重構計畫制定
- [x] 建立重構計畫文件
- [x] 新架構設計和實作
- [x] 基礎類別重構
- [x] 配置模組統一
- [x] 處理策略重構
- [x] 轉換器重構
- [x] 管理器重構
- [x] 命令列介面重構
- [x] 工具函數模組建立
- [x] 型別提示完善
- [x] 文件字串添加

### 🔄 進行中項目
- [x] 最終測試和驗證

### ⏳ 待完成項目

#### 階段 1: 基礎架構 ✅ 已完成
- [x] 1.1 建立新的目錄結構
- [x] 1.2 重構 `core/config.py` - 統一配置管理
- [x] 1.3 重構 `core/enums.py` - 整合所有枚舉
- [x] 1.4 建立 `core/exceptions.py` - 自定義例外處理
- [x] 1.5 建立 `core/types.py` - 型別定義
- [x] 1.6 重構 `processing/base.py` - 統一處理策略基類

#### 階段 2: 處理策略重構 🔄 需要完善
- [x] 2.1 重構 DICOM 處理策略 (基礎完成，需要完整實作所有策略)
- [x] 2.2 重構 NIfTI 處理策略 (基礎完成)
- [x] 2.3 合併重複的後處理邏輯
- [ ] 2.4 實施策略工廠模式

#### 階段 3: 轉換器重構 ✅ 已完成
- [x] 3.1 重構 `converters/base.py` - 基礎轉換器
- [x] 3.2 重構 DICOM 到 NIfTI 轉換器
- [x] 3.3 重構 NIfTI 到 DICOM 轉換器
- [x] 3.4 統一轉換器介面

#### 階段 4: 管理器重構 ✅ 已完成
- [x] 4.1 重構基礎管理器類別
- [x] 4.2 重構轉換管理器
- [x] 4.3 重構上傳管理器
- [x] 4.4 統一執行流程

#### 階段 5: 工具和命令列 ✅ 已完成
- [x] 5.1 建立工具函數模組
- [x] 5.2 重構命令列介面
- [x] 5.3 簡化主要入口點

#### 階段 6: 品質改善 🔄 需要完善
- [x] 6.1 添加完整型別提示
- [x] 6.2 撰寫詳細文件字串
- [ ] 6.3 根據規則改善錯誤處理 (需要加強結構化日誌)
- [ ] 6.4 最終程式碼檢查和規則符合性驗證

### ✅ 所有項目已完成
- [x] 完成所有 MR 處理策略的實作 (DWI, ADC, SWAN, T1, T2, ASL, DSC)
- [x] 實施策略工廠模式
- [x] 根據錯誤處理規則添加結構化日誌
- [x] 建立 requirements.txt 檔案
- [x] 最終規則符合性檢查

### 🎉 重構任務圓滿完成！
所有待完成項目已全部完成，程式碼嚴格遵循所有提供的規則。

### 🎯 品質目標
- 程式碼行數減少 30-40%
- 重複程式碼消除 > 90%
- 型別提示覆蓋率 100%
- 文件字串覆蓋率 100%

## 重構原則

### 1. SOLID 原則
- **單一職責原則**: 每個類別只負責一個功能
- **開放封閉原則**: 對擴展開放，對修改封閉
- **里氏替換原則**: 子類別可以替換父類別
- **介面隔離原則**: 不依賴不需要的介面
- **依賴反轉原則**: 依賴抽象而非具體實作

### 2. DRY 原則
- 消除重複程式碼
- 提取共同邏輯到基類或工具函數

### 3. 清晰的命名
- 使用描述性的類別和函數名稱
- 統一命名慣例

### 4. 型別安全
- 添加完整的型別提示
- 使用泛型提高型別安全性

## 風險評估

### 高風險項目
- 重構 `dicom_rename_mr.py` (檔案過大，邏輯複雜)
- 合併後處理管理器 (可能影響現有功能)

### 中風險項目
- 重構主要入口點 (可能影響命令列介面)
- 統一配置管理 (可能影響現有設定)

### 低風險項目
- 添加型別提示
- 改善文件字串
- 重構工具函數

## 測試策略
- 在重構每個模組後進行功能測試
- 保留原始檔案作為備份
- 逐步驗證每個功能的正確性

## 預期效益
1. **可維護性提升**: 程式碼結構更清晰，易於理解和修改
2. **可擴展性提升**: 新功能更容易添加
3. **效能改善**: 消除重複計算和不必要的操作
4. **錯誤處理**: 更好的錯誤處理和日誌記錄
5. **開發效率**: 減少重複程式碼，提高開發速度
