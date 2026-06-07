from models import Place
from osrm import OSRMClient

start = Place("清華大學", (24.7961, 120.9966))
end = Place("清大胖達咖啡", (24.7924, 120.9940))

osrm = OSRMClient()
route = osrm.get_route_with_fallback(start, end)

print(route["status"])
print("距離：", route["distance_km"], "km")
print("時間：", route["duration_min"], "min")
print("路線點數：", len(route["route_coords"]) if route["route_coords"] else 0)