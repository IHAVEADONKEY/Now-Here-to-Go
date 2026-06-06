from math import radians, sin, cos, sqrt, asin
from typing import Optional, Tuple, Dict, Any, List


class Place:
    """
    A class representing a location/place in the Smart City Navigator.

    Attributes:
        name: Name of the place
        coords: Tuple of (latitude, longitude)
        rating: Rating from 0-5 (optional)
        category: Category like 'restaurant', 'cafe' (optional)
    """

    def __init__(
        self,
        name: str,
        coords: Tuple[float, float],
        rating: Optional[float] = None,
        category: Optional[str] = None,
        time_tag: str = "both", # 在課程範本外在加上我們的 time_tag
        is_fallback: bool = False # 將 is_fallback 預設為 False
    ):
        """
        Initialize a Place.

        Args:
            name: Name of the place
            coords: Tuple of (latitude, longitude)
            rating: Optional rating (0-5)
            category: Optional category string
        """
        self.name = name
        self.coords = coords
        self._rating = None
        self.rating = rating  # Use setter for validation
        self.category = category
        self.time_tag = time_tag
        self.is_fallback = is_fallback

    # === Properties ===

    @property
    def lat(self) -> float:
        """Latitude coordinate."""
        return self.coords[0]

    @property
    def lon(self) -> float:
        """Longitude coordinate."""
        return self.coords[1]

    @property
    def rating(self) -> Optional[float]:
        """Place rating (0-5)."""
        return self._rating

    @rating.setter
    def rating(self, value: Optional[float]) -> None:
        """Set rating with validation."""
        if value is not None:
            if not isinstance(value, (int, float)):
                raise TypeError("Rating must be a number")
            if not 0 <= value <= 5:
                raise ValueError("Rating must be between 0 and 5")
        self._rating = value

    # === Instance Methods ===

    def distance_to(self, other: 'Place') -> float:
        """
        Calculate Haversine distance to another Place.

        Args:
            other: Another Place object

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in km

        lat1, lon1 = radians(self.lat), radians(self.lon)
        lat2, lon2 = radians(other.lat), radians(other.lon)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        return R * c

    def walking_time_to(self, other: 'Place', speed_kmh: float = 5.0) -> float:
        """
        Calculate walking time to another Place.

        Args:
            other: Another Place object
            speed_kmh: Walking speed in km/h (default 5.0)

        Returns:
            Walking time in minutes
        """
        distance = self.distance_to(other)
        return (distance / speed_kmh) * 60

    def to_dict(self) -> Dict[str, Any]:
        """Convert Place to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "coords": list(self.coords),
            "rating": self.rating,
            "category": self.category,
            "time_tag": self.time_tag,
            "is_fallback": self.is_fallback
        }

    # === Class Methods ===

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Place':
        """
        Create a Place from a dictionary.

        Args:
            data: Dictionary with place data

        Returns:
            New Place instance
        """
        return cls(
            name=data["name"],
            coords=tuple(data["coords"]),
            rating=data.get("rating"),
            category=data.get("category"),
            time_tag=data.get("time_tag", "both"),
            is_fallback=data.get("is_fallback", False)
        )

    @classmethod
    def from_nominatim(cls, data: Dict[str, Any]) -> 'Place':
        """
        Create a Place from Nominatim API response.

        Args:
            data: Nominatim search result

        Returns:
            New Place instance
        """
        return cls(
            name=data.get("display_name", "Unknown"),
            coords=(float(data["lat"]), float(data["lon"])),
            category=data.get("type"),
            time_tag="both", # 都先預測是 both
            is_fallback=False # 保證抓到的是即時資料
        )

    # === Special Methods ===

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Place('{self.name}', {self.coords}, rating={self.rating})"

    def __str__(self) -> str:
        """User-friendly string."""
        parts = [self.name]
        if self.rating is not None:
            parts.append(f"({self.rating}★)")
        if self.category:
            parts.append(f"[{self.category}]")
        return " ".join(parts)

    def __eq__(self, other: object) -> bool:
        """Check equality based on name and coordinates."""
        if not isinstance(other, Place):
            return NotImplemented
        return self.name == other.name and self.coords == other.coords

    def __hash__(self) -> int:
        """Make Place hashable."""
        return hash((self.name, self.coords))

    def __lt__(self, other: 'Place') -> bool:
        """Compare by rating for sorting."""
        if self.rating is None:
            return True
        if other.rating is None:
            return False
        return self.rating < other.rating