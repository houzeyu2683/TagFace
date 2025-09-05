# TagFace

一個基於人工智慧的影片人臉偵測與片段分割工具，能夠自動從 YouTube 播放清單下載影片，進行人臉偵測和追蹤，並智能分割出包含特定人臉的影片片段。

## 功能特色

- **YouTube 影片批次下載**：支援從 YouTube 播放清單批次下載影片
- **智慧人臉偵測**：使用先進的人臉偵測演算法，準確識別影片中的人臉
- **人臉追蹤技術**：基於 IoU 和結構相似性的連續性分析，實現穩定的人臉追蹤
- **自動影片分割**：根據人臉出現的時間區間，自動分割出相關影片片段
- **多行程並行處理**：支援多核心並行處理，提升處理效率
- **GPU 加速**：支援 CUDA GPU 加速，大幅提升處理速度

## 系統需求

### 硬體需求
- **GPU**：建議使用支援 CUDA 的 NVIDIA 顯示卡（可選，但強烈建議）
- **記憶體**：建議 8GB 以上 RAM
- **儲存空間**：足夠儲存下載影片和輸出片段的磁碟空間

### 軟體需求
- **Python**：3.7 或更高版本
- **作業系統**：Windows, macOS, Linux

### 相依套件
```
torch
torchvision
face_alignment
moviepy
yt_dlp
pandas
numpy
PIL
scikit-image
tqdm
```

## 安裝指南

1. **複製專案**
```bash
git clone https://github.com/yourusername/TagFace.git
cd TagFace
```

2. **安裝相依套件**
```bash
pip install torch torchvision face_alignment moviepy yt_dlp pandas numpy pillow scikit-image tqdm
```

3. **安裝 FFmpeg**（影片處理必需）
- Windows: 下載 FFmpeg 並加入系統 PATH
- macOS: `brew install ffmpeg`
- Linux: `sudo apt install ffmpeg`

## 使用方法

### 1. 下載影片

編輯 `script-download-video.py`，設定 YouTube 播放清單連結：

```python
import core

link = 'https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID'
folder = './download/YOUR_FOLDER_NAME'
video = core.Video(link, folder)
video.searchCatalog(query=None)  # 可使用 pandas query 語法過濾影片
video.saveCatalog()
```

執行下載：
```bash
python script-download-video.py
```

### 2. 人臉偵測與影片分割

編輯 `script-cut-video.py`，設定處理參數：

```python
import core

engine = core.Engine(folder='./episode/YOUR_OUTPUT_FOLDER')
engine.processBatch(
    channel='./download/YOUR_FOLDER_NAME/video', 
    core=2  # 並行處理核心數
)
```

執行處理：
```bash
python script-cut-video.py
```

### 輸出格式

處理完成後，會在指定的輸出資料夾中產生：

- **segment.json**：包含所有偵測到的人臉片段資訊
  ```json
  {
    "0": [[0.0, 4.0], [1305, 138, 1434, 308]],
    "5": [[9.0, 10.0], [1118, 154, 1252, 314]]
  }
  ```
  格式：`"片段ID": [[開始時間, 結束時間], [x1, y1, x2, y2]]`

- **video/** 資料夾：包含分割後的影片片段檔案

## 專案結構

```
TagFace/
├── core/                           # 核心模組
│   ├── __init__.py
│   ├── _engine_.py                 # 人臉偵測引擎
│   └── _video_.py                  # 影片下載模組
├── beta/                           # 測試版本模組
├── download/                       # 下載的原始影片
│   └── [playlist_id]/
│       ├── catalog.csv             # 播放清單資訊
│       └── video/                  # 下載的影片檔案
├── episode/                        # 分割後的影片片段
│   └── [playlist_id]/
│       └── [video_id]/
│           ├── segment.json        # 片段資訊
│           └── video/              # 分割的影片檔案
├── script-download-video.py        # 影片下載腳本
├── script-cut-video.py            # 影片分割腳本
├── LICENSE                         # 授權檔案
└── README.md                       # 說明檔案
```

## 技術細節

### 人臉偵測演算法

- **模型**：使用 face_alignment 函式庫的 2D 人臉關鍵點偵測模型
- **設備**：支援 CUDA GPU 加速
- **偵測頻率**：每 25 幀偵測一次（可調整）

### 人臉追蹤演算法

本專案實現了基於多重指標的人臉追蹤演算法：

1. **IoU (Intersection over Union)**：計算相鄰幀中人臉邊界框的重疊度
   - 閾值：0.6
   - 用於判斷是否為同一人臉的基本指標

2. **結構相似性 (SSIM)**：比較人臉區域的圖像相似性
   - 閾值：0.8
   - 提供更精確的相似性判斷

### 影片處理流程

1. **影片載入**：使用 MoviePy 載入影片，驗證格式和品質
2. **人臉偵測**：在指定間隔的幀上執行人臉偵測
3. **軌跡追蹤**：使用連續性分析建立人臉軌跡
4. **片段分割**：根據軌跡時間範圍分割影片
5. **檔案輸出**：使用 FFmpeg 進行高效率的影片編碼

### 效能優化

- **多行程處理**：支援多核心並行處理多個影片
- **GPU 加速**：人臉偵測使用 CUDA 加速
- **記憶體優化**：逐幀處理，避免載入完整影片到記憶體
- **智慧過濾**：自動過濾過短或品質不佳的片段

## 注意事項

1. **GPU 記憶體**：人臉偵測需要一定的 GPU 記憶體，建議 4GB 以上
2. **處理時間**：處理時間取決於影片長度、解析度和硬體效能
3. **儲存空間**：分割後的影片片段可能佔用大量儲存空間
4. **YouTube 政策**：請遵守 YouTube 的服務條款和版權政策

## 授權

本專案採用 Apache License 2.0 授權。詳細內容請參閱 [LICENSE](LICENSE) 檔案。

## 貢獻

歡迎提交 Issue 和 Pull Request 來改善這個專案！

---

**TagFace** - 讓影片人臉偵測變得簡單高效

後續改一下！