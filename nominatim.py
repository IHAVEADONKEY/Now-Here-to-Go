import requests
import time
from models import Place
from fallback_data import get_fallback_places
from functools import wraps

def rate_limit(seconds=1.0):
    """
    Decorator that ensures minimum time between function calls.

    Args:
        seconds: Minimum seconds between calls (default 1.0)
    """
    last_call_time = [0.0]  # Use list to allow modification in closure

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Calculate time since last call
            elapsed = time.time() - last_call_time[0]

            # If not enough time has passed, wait
            if elapsed < seconds:
                wait_time = seconds - elapsed
                print(f"Rate limiting: waiting {wait_time:.2f}s...")
                time.sleep(wait_time)

            # Execute the function
            result = func(*args, **kwargs)

            # Record this call time
            last_call_time[0] = time.time()

            return result

        return wrapper
    return decorator


class NominatimClient:
    """負責地點搜尋"""
    
    def __init__(self, user_agent="UrbanStroll/1.0 (cs101_student@nthu.edu.tw)"): # 這id再看要不要改
        self.headers = {"User-Agent": user_agent}

    @rate_limit(seconds=1.1)
    def geocode(self, location_text: str) -> tuple[float, float] | None:
        """
        將使用者輸入的起點文字 (例如 "清華大學") 轉換成座標。
        這是 search_nearby 的前置步驟。
        """
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": location_text, 
            "format": "json", 
            "limit": 1
        }
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
        except requests.exceptions.RequestException as e:
            print(f"[警告] Nominatim Geocode 連線異常: {e}")
            
        return None

    @rate_limit(seconds=1.1)
    def search_nearby(self, keyword: str, lat: float, lon: float) -> list[Place]:
        """
        接收前端傳來的關鍵字與座標進行搜尋。
        如果 API 失敗或找不到地點，將自動觸發預設候補機制 (Fallback)。
        """
        url = "https://nominatim.openstreetmap.org/search"
        
        # 只看距離1.5公里內的目標(漫步時間控制在15~20分鐘)
        viewbox = f"{lon-0.015},{lat-0.015},{lon+0.015},{lat+0.015}"
        params = {
            "q": keyword, 
            "format": "json", 
            "limit": 5, 
            "viewbox": viewbox, 
            "bounded": 1
        }
        
        try:
            # 找地點的時間控在5秒內，避免網路炸開
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            
            if response.status_code == 200:
                raw_data = response.json()
                
                # 成功找到
                if raw_data:
                    places = [Place.from_nominatim(item) for item in raw_data]

                    # 標記此資料為網路上的資料
                    for p in places:
                        p.is_fallback = False
                    return places
                    
        except requests.exceptions.RequestException as e:
            print(f"[警告] Nominatim API 連線異常: {e}")
            
        # 對於API可能壞掉，或raw_data是空的
        print(f"[提示] 無法獲取 '{keyword}' 即時資料，啟動 Fallback 備用地點。")
        
        fallback_places = get_fallback_places(keyword)
        
        for p in fallback_places:
            p.is_fallback = True
            
        return fallback_places
