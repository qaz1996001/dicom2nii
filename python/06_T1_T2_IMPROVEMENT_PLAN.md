# T1/T2 處理策略改進計畫

## 🎯 改進目標

### 1. 完善 T1ProcessingStrategy 功能
- 添加 REFORMATTED 影像類型檢查
- 實作完整的 T1CUBECE_AXIr、T1CUBE_AXIr 等重新格式化序列支援
- 遵循 .cursor 規則的 Python 開發原則

### 2. 完善 T2ProcessingStrategy 功能  
- 添加 REFORMATTED 影像類型檢查
- 實作完整的 T2CUBE_AXIr、T2CUBECE_AXIr 等重新格式化序列支援
- 確保與 T1 策略的一致性

### 3. 遵循 .cursor 規則
- 使用 uv 管理 Python 專案
- 遵循函數式、宣告式程式設計
- 使用描述性變數名稱
- 實施 RORO (Receive an Object, Return an Object) 模式

## 📋 發現的問題

### T1ProcessingStrategy 缺失功能
1. **REFORMATTED 檢查缺失**: 未檢查 `(0008,0008) Image Type` 是否包含 `REFORMATTED`
2. **重新格式化序列支援不完整**: 缺少 `T1CUBE_AXIr`、`T1CUBECE_AXIr` 等
3. **3D 序列字典不完整**: 需要添加所有 CUBE、BRAVO 的重新格式化變體

### T2ProcessingStrategy 缺失功能
1. **相同的 REFORMATTED 檢查問題**
2. **缺少 T2CUBE_AXIr、T2CUBECE_AXIr 等重新格式化序列**
3. **FLAIR CUBE 重新格式化支援缺失**

### .cursor 規則符合性問題
1. **專案管理**: 需要使用 uv 而非 pip
2. **函數式程式設計**: 需要更多純函數和宣告式程式設計
3. **RORO 模式**: 需要改善輸入/輸出物件設計

## 🛠️ 改進計畫

### 階段 1: 設定 uv 專案管理 ✅ 已完成
- [x] 1.1 建立 pyproject.toml 檔案
- [x] 1.2 使用 uv 初始化專案 (配置完成)
- [x] 1.3 遷移 requirements.txt 到 uv 格式
- [x] 1.4 設定開發依賴

### 階段 2: 改進 T1ProcessingStrategy ✅ 已完成
- [x] 2.1 添加 REFORMATTED 影像類型檢查邏輯
- [x] 2.2 完善 3D 重新格式化序列字典 (32 種組合)
- [x] 2.3 實作 get_image_orientation 方法 (包含 REFORMATTED)
- [x] 2.4 更新所有 CUBE/BRAVO 重新格式化變體

### 階段 3: 改進 T2ProcessingStrategy ✅ 已完成
- [x] 3.1 添加 REFORMATTED 影像類型檢查邏輯
- [x] 3.2 完善 3D 重新格式化序列字典 (24 種組合)
- [x] 3.3 實作與 T1 一致的處理邏輯
- [x] 3.4 添加 FLAIR CUBE 重新格式化支援

### 階段 4: .cursor 規則符合性 ✅ 已完成
- [x] 4.1 重構為更函數式的程式設計風格
- [x] 4.2 實施 RORO 模式 (ProcessingRequest/Result)
- [x] 4.3 改善變數命名 (使用輔助動詞 is_*, has_*)
- [x] 4.4 建立純函數輔助工具

### 階段 5: 驗證和測試 ✅ 已完成
- [x] 5.1 驗證 REFORMATTED 邏輯正確性
- [x] 5.2 測試所有重新格式化序列支援
- [x] 5.3 確保向後相容性
- [x] 5.4 完成功能驗證

## 🔍 REFORMATTED 邏輯分析

### 原始邏輯 (來自 base.py)
```python
@classmethod
def get_image_orientation(cls, dicom_ds: FileDataset):
    image_orientation = cls.image_orientation_processing_strategy.process(dicom_ds=dicom_ds)
    image_type = dicom_ds.get((0x08, 0x08))
    if image_type[2] == 'REFORMATTED':
        if image_orientation == ImageOrientationEnum.AXI:
            return ImageOrientationEnum.AXIr
        elif image_orientation == ImageOrientationEnum.SAG:
            return ImageOrientationEnum.SAGr
        elif image_orientation == ImageOrientationEnum.COR:
            return ImageOrientationEnum.CORr
        else:
            return image_orientation
    else:
        return image_orientation
```

### 需要實作的重新格式化序列

#### T1 重新格式化序列
- T1CUBE_AXIr, T1CUBE_CORr, T1CUBE_SAGr
- T1CUBECE_AXIr, T1CUBECE_CORr, T1CUBECE_SAGr  
- T1FLAIRCUBE_AXIr, T1FLAIRCUBE_CORr, T1FLAIRCUBE_SAGr
- T1FLAIRCUBECE_AXIr, T1FLAIRCUBECE_CORr, T1FLAIRCUBECE_SAGr
- T1BRAVO_AXIr, T1BRAVO_SAGr, T1BRAVO_CORr
- T1BRAVOCE_AXIr, T1BRAVOCE_SAGr, T1BRAVOCE_CORr

#### T2 重新格式化序列
- T2CUBE_AXIr, T2CUBE_CORr, T2CUBE_SAGr
- T2CUBECE_AXIr, T2CUBECE_CORr, T2CUBECE_SAGr
- T2FLAIRCUBE_AXIr, T2FLAIRCUBE_CORr, T2FLAIRCUBE_SAGr
- T2FLAIRCUBECE_AXIr, T2FLAIRCUBECE_SAGr, T2FLAIRCUBECE_CORr

## 🎯 .cursor 規則要求

### Python 開發原則
1. **函數式程式設計**: 偏向純函數，避免不必要的類別
2. **宣告式程式設計**: 清晰的意圖表達
3. **描述性變數名稱**: 使用輔助動詞 (is_active, has_permission)
4. **RORO 模式**: Receive an Object, Return an Object
5. **型別提示**: 所有函數簽名都要有型別提示
6. **Early Return**: 錯誤條件使用提早返回

### 專案管理
- **使用 uv**: 不使用 pip，改用 uv 管理依賴
- **pyproject.toml**: 現代化的專案配置

## 🚀 預期改進效果

1. **功能完整性**: 支援所有 REFORMATTED 序列類型
2. **規則符合性**: 100% 遵循 .cursor 規則
3. **程式碼品質**: 更函數式、更易讀的程式碼
4. **專案管理**: 現代化的 uv 專案管理
