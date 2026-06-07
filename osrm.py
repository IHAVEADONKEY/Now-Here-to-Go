import requests
from models import Place

class OSRMClient:
    """負責向 OSRM 請求步行路線規劃的後端引擎"""

    def __init__(self):
        # 選擇 foot 模式
        self.base_url = "http://router.project-osrm.org/route/v1/walking"

    def get_walking_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> dict:
        """
        取得從起點到終點的步行路線。
        """
        coordinates = f"{start_lon},{start_lat};{end_lon},{end_lat}"
        url = f"{self.base_url}/{coordinates}"

        params = {
            "overview": "full",        # 要求回傳完整的路線軌跡
            "geometries": "geojson"    # 拿 GeoJSON 格式
        }

        try:
            # 設定 timeout 5 秒
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == "Ok" and len(data.get("routes", [])) > 0:
                    # 抓取第一條最佳路線
                    route = data["routes"][0]

                    # 提取距離 (公尺) 
                    distance_m = route["distance"]
                    geometry = route["geometry"] 

                    # 轉換為使用者好讀的單位 (公里)
                    distance_km = round(distance_m / 1000, 2)

                    # 假設人類漫步時速約 5.0 km/h
                    duration_min = round((distance_km / 5.0) * 60)

                    # 先緯度再經度
                    flipped_coords = [[lat, lon] for lon, lat in geometry["coordinates"]]

                    return {
                        "status": "success",
                        "distance_km": distance_km,
                        "duration_min": duration_min,
                        "route_coords": flipped_coords
                    }

            print(f"[警告] OSRM 回傳異常狀態碼: {response.status_code}")
            return {"status": "error", "message": "路線規劃失敗"}

        except requests.exceptions.RequestException as e:
            print(f"[警告] OSRM API 連線異常: {e}")
            return {"status": "error", "message": "網路異常"}
        
    def get_fallback_estimate(self, start: Place, end: Place) -> dict:
        """OSRM 失敗時，用 Haversine 距離給出估算"""
        distance_km = start.distance_to(end)
        duration_min = round(start.walking_time_to(end))
        return {
            "status": "fallback",
            "distance_km": round(distance_km, 2),
            "duration_min": duration_min,
            "route_coords": None  # 前端不畫路線，只顯示估算
        }
    
    def get_route_with_fallback(self, start: Place, end: Place) -> dict:
        """
        呼叫寫好的 get_walking_route。
        若網路異常導致回傳 error，則啟動降級方案。
        """

        result = self.get_walking_route(start.lat, start.lon, end.lat, end.lon)
        
        # 攔截錯誤，啟動降級
        if result["status"] == "error":
            print(f"[提示] OSRM 導航失效，啟用 Haversine 直線距離降級方案。")
            return self.get_fallback_estimate(start, end)
            
        return result