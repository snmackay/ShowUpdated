import os
import re
import requests
import json
from rapidfuzz import fuzz




#retrieve API key from config.json
def getKey(config):
    with open(config,'r') as f:
        contents=json.load(f)
        return contents["apiKey"]

#globals
TVDB_API_KEY = getKey("config.json")
TVDB_LOGIN_URL = "https://api4.thetvdb.com/v4/login"
TVDB_SEARCH_URL = "https://api4.thetvdb.com/v4/search"
TVDB_SERIES_EXTENDED_URL = "https://api4.thetvdb.com/v4/series/{id}/extended"


# -------------------- Grab Year --------------------
def extract_year(folder_name: str) -> int | None:
    match = re.search(r"\b(19\d{2}|20\d{2})\b", folder_name)
    return int(match.group(1)) if match else None

# -------------------- Clean File Name --------------------
def clean_folder_name(folder_name: str) -> str:
    name = os.path.basename(folder_name)

    patterns = [
        r"\bS\d{1,2}E\d{1,2}\b",
        r"\bS\d{1,2}\b",
        r"\b(720p|1080p|2160p|4k)\b",
        r"\b(x264|x265|h264|h265|hevc)\b",
        r"\b(bluray|web[-_. ]?dl|webrip|hdr)\b"
    ]

    for p in patterns:
        name = re.sub(p, "", name, flags=re.IGNORECASE)

    # Remove year only after extraction
    name = re.sub(r"\b(19\d{2}|20\d{2})\b", "", name)

    name = re.sub(r"[._\-]+", " ", name)
    return name.strip()

# -------------------- Get Session Token --------------------
def get_tvdb_token() -> str:
    response = requests.post(
        TVDB_LOGIN_URL,
        json={"apikey": TVDB_API_KEY},
        timeout=10
    )
    response.raise_for_status()
    return response.json()["data"]["token"]

# -------------------- Search TV Show --------------------
def search_tv_show(query: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "series", "limit": 10}

    response = requests.get(
        TVDB_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=10
    )
    response.raise_for_status()

    return response.json().get("data", [])   

# -------------------- Grab List of Seasons --------------------
def get_tvdb_seasons(tvdb_id: int, token: str) -> set:
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(
        TVDB_SERIES_EXTENDED_URL.format(id=tvdb_id),
        headers=headers,
        timeout=10
    )
    response.raise_for_status()

    seasons = set()
    for season in response.json()["data"].get("seasons", []):
        number = season.get("number")
        if isinstance(number, int) and number > 0:
            seasons.add(number)

    return seasons

# -------------------- Fuzzy Matching --------------------
def score_match(query: str, folder_year: int | None, candidate: dict) -> int:
    title = candidate.get("name", "")
    aliases = candidate.get("aliases", []) or []

    # Base fuzzy score
    scores = [
        fuzz.token_sort_ratio(query, title),
        fuzz.partial_ratio(query, title)
    ]

    for alias in aliases:
        scores.append(fuzz.token_sort_ratio(query, alias))

    score = max(scores)

    # ---- SAFE YEAR HANDLING ----
    candidate_year = candidate.get("year")

    try:
        candidate_year = int(candidate_year)
    except (TypeError, ValueError):
        candidate_year = None

    if folder_year and candidate_year:
        diff = abs(folder_year - candidate_year)
        if diff == 0:
            score += 20
        elif diff <= 1:
            score += 10
        else:
            score -= 10

    return min(score, 100)



# -------------------- Handles Picking Right Match --------------------
def pick_best_match(query: str, folder_year: int | None, results: list):
    scored = [
        (score_match(query, folder_year, r), r)
        for r in results
    ]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0] if scored else None


# -------------------- Check Local Seasons --------------------
def get_local_seasons(show_path: str) -> set:
    season_pattern = re.compile(r"(season|s)\s*(\d+)", re.IGNORECASE)
    seasons = set()

    for entry in os.listdir(show_path):
        full_path = os.path.join(show_path, entry)
        if os.path.isdir(full_path):
            match = season_pattern.search(entry)
            if match:
                seasons.add(int(match.group(2)))

    return seasons
