from models import Place
import copy

# 心情轉關鍵字
MOOD_KEYWORDS = {
    "tired":      ["cafe", "park"],
    "lonely":     ["bookstore", "riverside", "cafe"],
    "calm":       ["park", "garden"],
    "energetic":  ["night market", "plaza", "shopping area"],
    "escape":     ["riverside", "viewpoint", "park"],
    "night walk": ["night view", "bar", "night market"]
}

FALLBACK_PLACES = {
    "cafe": [
        Place("清大胖達咖啡", (24.792431, 120.994059), rating=4.5, category="cafe", time_tag="both"),
        Place("江山藝改所", (24.799182, 120.965921), rating=4.4, category="cafe", time_tag="both"),
        Place("九慕咖啡", (24.804946, 120.970126), rating=4.5, category="cafe", time_tag="day")
    ],
    "park": [
        Place("清大成功湖畔", (24.7942708563, 120.99500298), rating=4.7, category="park", time_tag="both"),
        Place("護城河親水公園", (24.806493, 120.970706), rating=4.3, category="park", time_tag="both"),
        Place("十八尖山入口", (24.791536, 120.978476), rating=4.5, category="park", time_tag="day")
    ],
    "garden": [
        Place("新竹公園", (24.800915, 120.977325), rating=4.4, category="garden", time_tag="day")
    ],
    "bookstore": [
        Place("清大水木書苑", (24.792333, 120.994652), rating=4.4, category="bookstore", time_tag="day"),
        Place("玫瑰色二手書店", (24.804483, 120.961851), rating=4.8, category="bookstore", time_tag="both")
    ],
    "riverside": [
        Place("隆恩圳親水空間", (24.808240, 120.974782), rating=4.4, category="riverside", time_tag="both"),
        Place("頭前溪左岸休憩公園", (24.821639, 120.990277), rating=4.7, category="riverside", time_tag="day")
    ],
    "viewpoint": [
        Place("新竹17公里海岸風景區", (24.846239, 120.925893), rating=4.3, category="viewpoint", time_tag="day"),
        Place("青草湖風景區", (24.774887, 120.969859), rating=4.4, category="viewpoint", time_tag="day")
    ],
    "night market": [
        Place("清大夜市", (24.796464, 120.998389), rating=4.1, category="night_market", time_tag="night"),
        Place("新竹後站夜市", (24.800959, 120.974222), rating=4.3, category="night_market", time_tag="night")
    ],
    "plaza": [
        Place("迎曦門", (24.804176, 120.970224), rating=4.3, category="plaza", time_tag="both"),
        Place("城隍廟廣場", (24.804709, 120.965957), rating=4.4, category="plaza", time_tag="both")
    ],
    "shopping area": [
        Place("Big City 遠東巨城", (24.809816, 120.975132), rating=4.4, category="shopping", time_tag="both"),
        Place("中正台商圈", (24.803240, 120.968561), rating=3.7, category="shopping", time_tag="night")
    ],
    "night view": [
        Place("東門城夜景", (24.804176, 120.970224), rating=4.3, category="night_view", time_tag="night"),
        Place("南寮漁港 (夜間)", (24.848332, 120.930273), rating=4.2, category="night_view", time_tag="night")
    ],
    "bar": [
        Place("Eternal Area-光之迴廊", (24.802624, 120.969729), rating=4.7, category="bar", time_tag="night"),
        Place("Bar Reviver", (24.800917, 120.968808), rating=4.6, category="bar", time_tag="night")
    ]
}

def get_fallback_places(keyword: str) -> list[Place]:
    """
    根據 API 搜尋的關鍵字，取得對應的備用地點。
    若無完全對應的關鍵字，預設回傳「公園」確保系統永遠有安全的地點可顯示。
    """
    # 將關鍵字轉小寫以防大小寫問題
    keyword_lower = keyword.lower()
    originals = FALLBACK_PLACES.get(keyword_lower, FALLBACK_PLACES["park"])
    return [copy.copy(p) for p in originals]