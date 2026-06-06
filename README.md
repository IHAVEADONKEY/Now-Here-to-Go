# Now Here to Go 📍 城市漫遊系統

> 「不要問目的地在哪，問問你現在的心情。」

**Now Here to Go** 是一個結合「情緒」與「城市探索」的變相導航系統。捨棄傳統 A 點到 B 點的效率導航，使用者只需選擇當下的心情（Tired, Lonely, Energetic）與出發點，系統便會自動在步行 15-20 分鐘（約 1.5 公里）的舒適範圍內，為你推薦最適合的避風港，並繪製專屬的漫步路線。

---

## ✨ 核心架構與工程亮點

本系統後端採模組化設計，具備極高的容錯率（Fault Tolerance）與防呆機制：

* **🧠 搜尋大腦 (`nominatim.py`)**
  * 結合 OpenStreetMap Nominatim API，利用 `viewbox` 嚴格限制搜尋半徑。
  * 內建 **Rate Limit 裝飾器**，防止請求過載。
  * 具備 **文字轉座標 (Geocode)** 能力。
* **🚶 路線雙腿 (`osrm.py`)**
  * 介接 OSRM (Open Source Routing Machine) 進行真實街道的步行軌跡計算。
  * 具備 **無縫降級方案 (Fallback)**：若遇網路斷線或 API 失效，自動切換為 Haversine 公式進行直線距離與時間估算。
* **🛡️ 絕對防禦 (`fallback_data.py`)**
  * 內建新竹市區與清大周邊的精選備用地點。當 API 查無資料時，確保系統永不當機。
  * 具備淺複製 (Shallow Copy) 保護機制，防止共用記憶體污染，並為每個地點打上日/夜時間標籤 (`time_tag`)。
* **💾 記憶中樞 (`storage.py`)**
  * 輕量級的 JSON 本機資料持久化方案，負責「我的最愛」的新增、讀取與刪除。
* **📐 資料骨架 (`models.py`)**
  * 嚴謹的 `Place` 類別定義，封裝了經緯度處理與數學距離計算邏輯。

---

## 📄 資料格式與串接規格 (API Spec)

提供給前端整合 UI 時參考的資料結構，所有後端模組皆以此格式進行資料拋接。

### 1. 地點卡片資料 (Place Object)
搜尋推薦地點（網路即時或 Fallback 備用）皆會統一轉換為此格式：
```json
{
  "name": "清大胖達咖啡",
  "coords": [24.7924, 120.9940], 
  "rating": 4.5,
  "category": "cafe",
  "time_tag": "both",        // 包含: "day", "night" 或 "both"，用於 UI 變化
  "is_fallback": false       // 若為 true，代表 API 無回應，已啟用本地備用資料
}

```

### 2. 導航路線資料 (OSRM Routing)

將起終點座標送入 `osrm.py` 後，會回傳以下字典供前端渲染地圖：

```json
{
  "status": "success",       // 若為 "fallback"，代表網路斷線，已啟用直線距離估算
  "distance_km": 1.2,        // 供卡片顯示之預估距離
  "duration_min": 15,        // 供卡片顯示之預估步行時間
  "route_coords": [          // 供 Leaflet 地圖套件繪製折線的座標陣列
    [24.79, 120.99], 
    [24.80, 120.98]
  ] 
}

```

### 3. 本機收藏功能 (Local Storage)

* **新增/刪除**：將上述的 `Place Object` 傳入 `storage.py` 的對應函數即可寫入 `favorites.json`。
* **讀取**：回傳值為由 `Place Object` 組成的 List。

---

## 🚀 快速啟動 (Quick Start)

### 1. 環境需求

請確保已安裝 Python 3.x，並安裝 requests 套件（後續整合將加入 Flask）：

```bash
pip install requests

```

### 2. 模組測試

各模組皆可獨立引入與測試，例如：

```python
from nominatim import NominatimClient
nom_client = NominatimClient()
places = nom_client.search_nearby("cafe", 24.7961, 120.9966)

```

## 🛠️ 技術棧 (Tech Stack)

* **Backend**: Python 3, Requests
* **External APIs**: Nominatim (Geocoding), OSRM (Routing)
* **Storage**: Local JSON
