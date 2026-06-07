from flask import Flask, render_template, request, jsonify
from models import Place
from nominatim import NominatimClient
from osrm import OSRMClient

app = Flask(__name__)

nom_client = NominatimClient()
osrm_client = OSRMClient()

MOOD_DATA = {
    "Tired": {
        "keywords": ["cafe", "park"],
        "music": "soft piano",
        "theme": "tired"
    },
    "Lonely": {
        "keywords": ["bookstore", "cafe", "riverside"],
        "music": "melancholic piano",
        "theme": "lonely"
    },
    "Calm": {
        "keywords": ["park", "garden", "cafe"],
        "music": "ambient piano",
        "theme": "calm"
    },
    "Energetic": {
        "keywords": ["night market", "plaza", "shopping area"],
        "music": "uplifting instrumental",
        "theme": "energetic"
    },
    "Escape": {
        "keywords": ["park", "viewpoint", "riverside"],
        "music": "cinematic piano",
        "theme": "escape"
    },
    "Night Walk": {
        "keywords": ["night market", "bar", "riverside"],
        "music": "lo-fi night piano",
        "theme": "night"
    }
}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/recommend", methods=["POST"])
def recommend():
    data = request.json
    mood = data.get("mood")
    start_text = data.get("start")

    coords = nom_client.geocode(start_text)
    if coords is None:
        return jsonify({"error": "找不到起點，請換一個地點名稱"}), 400

    start_place = Place(start_text, coords)
    mood_info = MOOD_DATA[mood]

    candidates = []

    for keyword in mood_info["keywords"]:
        places = nom_client.search_nearby(keyword, coords[0], coords[1])
        for p in places:
            distance = start_place.distance_to(p)
            item = p.to_dict()
            item["distance_km"] = round(distance, 2)
            candidates.append(item)

    candidates = sorted(candidates, key=lambda x: x["distance_km"])[:6]

    return jsonify({
        "start": {
            "name": start_text,
            "coords": list(coords)
        },
        "mood": mood,
        "theme": mood_info["theme"],
        "music": mood_info["music"],
        "places": candidates
    })


@app.route("/api/route", methods=["POST"])
def route():
    data = request.json

    start_data = data["start"]
    end_data = data["end"]

    start = Place(start_data["name"], tuple(start_data["coords"]))
    end = Place(
        end_data["name"],
        tuple(end_data["coords"]),
        category=end_data.get("category"),
        time_tag=end_data.get("time_tag", "both"),
        is_fallback=end_data.get("is_fallback", False)
    )

    route_data = osrm_client.get_route_with_fallback(start, end)

    return jsonify(route_data)


if __name__ == "__main__":
    app.run(debug=True)