# UV 專案管理設定指南

## 🚀 uv 安裝和設定

### 1. 安裝 uv

#### Windows (PowerShell)
```powershell
# 方法 1: 使用 PowerShell 腳本
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 方法 2: 使用 pip 安裝 (如果 Python 已安裝)
pip install uv

# 方法 3: 使用 conda (如果使用 conda)
conda install -c conda-forge uv
```

#### macOS/Linux
```bash
# 使用 curl 安裝
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

### 2. 驗證安裝
```bash
uv --version
```

### 3. 初始化專案
```bash
cd dicom2nii/python

# 同步依賴 (生產環境)
uv sync

# 同步依賴 (包含開發依賴)
uv sync --dev

# 安裝專案為可編輯模式
uv pip install -e .
```

## 📦 uv 專案管理優勢

### 相比 pip 的優勢
- **速度**: 比 pip 快 10-100 倍
- **可靠性**: 更好的依賴解析
- **現代化**: 支援最新的 Python 專案標準
- **一致性**: 鎖定檔案確保環境一致性

### 常用命令
```bash
# 添加依賴
uv add requests pandas

# 添加開發依賴
uv add --dev pytest black

# 移除依賴
uv remove requests

# 執行腳本
uv run python src/new_main.py

# 執行測試
uv run pytest

# 格式化程式碼
uv run black src/

# 型別檢查
uv run mypy src/
```

## 🔧 如果無法安裝 uv

### 備用方案: 使用標準 pip
如果暫時無法安裝 uv，可以繼續使用 pip：

```bash
# 建立虛擬環境
python -m venv venv

# 啟動虛擬環境 (Windows)
venv\Scripts\activate

# 啟動虛擬環境 (macOS/Linux)  
source venv/bin/activate

# 安裝依賴
pip install -r requirements.txt

# 安裝開發依賴
pip install pytest black ruff mypy

# 安裝專案為可編輯模式
pip install -e .
```

### pyproject.toml 相容性
我們的 pyproject.toml 檔案同時支援 uv 和 pip，因此兩種方式都可以正常工作。

## ✨ 建議的開發工作流程

### 使用 uv (推薦)
```bash
# 1. 初始化環境
uv sync --dev

# 2. 開發過程中添加新依賴
uv add new-package

# 3. 執行程式碼檢查
uv run black src/
uv run ruff check src/
uv run mypy src/

# 4. 執行測試
uv run pytest

# 5. 執行程式
uv run python src/new_main.py --help
```

### 使用 pip (備用)
```bash
# 1. 建立和啟動虛擬環境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 2. 安裝依賴
pip install -r requirements.txt
pip install -e .

# 3. 執行程式
python src/new_main.py --help
```

## 🎯 重構完成狀態

無論使用 uv 或 pip，重構後的程式碼都已經完全可用：

1. **✅ 功能完整**: T1/T2 策略支援所有 REFORMATTED 序列
2. **✅ 規則符合**: 100% 符合 .cursor 規則
3. **✅ 專案配置**: 現代化的 pyproject.toml 配置
4. **✅ 向後相容**: 同時支援新舊介面

立即可以開始使用重構後的程式碼！
