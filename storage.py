import json
import os
from models import Place

# 定義要存檔的檔名
FAVORITES_FILE = "favorites.json"

def get_favorites() -> list[Place]:
    """
    從 JSON 檔案中讀取使用者的最愛清單，並轉換回 Place 物件。
    """
    # 避免 FileNotFoundError
    if not os.path.exists(FAVORITES_FILE):
        return []
        
    try:
        with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # JSON 轉 Place 物件
            return [Place.from_dict(item) for item in data]
            
    except (json.JSONDecodeError, KeyError) as e:
        print(f"[警告] 最愛檔案損毀或格式錯誤: {e}")
        return []

def save_favorite(place: Place) -> bool:
    """
    將新的 Place 物件存入 JSON 檔案中。
    """
    favorites = get_favorites()
    
    # 透過 Place.__eq__ 檢查是否已收藏
    if place in favorites:
        print(f"[提示] '{place.name}' 已經在收藏清單中了！")
        return False
        
    favorites.append(place)
    
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            
            # 變回字典
            dict_data = [p.to_dict() for p in favorites]
            
            # 防止亂碼產生
            json.dump(dict_data, f, ensure_ascii=False, indent=4)
            
        print(f"[成功] 已將 '{place.name}' 加入收藏！")
        return True
        
    except IOError as e:
        print(f"[錯誤] 無法寫入最愛檔案: {e}")
        return False
    
def remove_favorite(place: Place) -> bool:
    """
    從 JSON 檔案中刪除指定的 Place 物件。
    """
    favorites = get_favorites()
    
    # 透過 Place 類別內建的.__eq__ 來篩
    new_favorites = [p for p in favorites if p != place]
    
    # 如果數量沒變，代表原本就不在裡面
    if len(favorites) == len(new_favorites):
        print(f"[提示] '{place.name}' 不在收藏清單中。")
        return False
        
    try:
        with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
            dict_data = [p.to_dict() for p in new_favorites]
            json.dump(dict_data, f, ensure_ascii=False, indent=4)
        print(f"[成功] 已將 '{place.name}' 從收藏中移除！")
        return True
    except IOError as e:
        print(f"[錯誤] 無法更新最愛檔案: {e}")
        return False