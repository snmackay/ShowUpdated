import os
import re
import json
import requests
from rapidfuzz import fuzz

#retrieve API key from config.json
def getKey(config):
    with open(config,'r') as f:
        contents=json.loads(f)
        return contents["apiKey"]

TVDB_API_KEY = getKey("config.json")

TVDB_LOGIN_URL = "https://api4.thetvdb.com/v4/login"
TVDB_SEARCH_URL = "https://api4.thetvdb.com/v4/search"
TVDB_SERIES_EXTENDED_URL = "https://api4.thetvdb.com/v4/series/{id}/extended"


# Cleans Up a File Name 

def clean_folder_name(folder_name: str) -> str:
    name = os.path.basename(folder_name)

    patterns = [
        r"\bS\d{1,2}E\d{1,2}\b",
        r"\bS\d{1,2}\b",
        r"\b\d{4}\b",
        r"\b(720p|1080p|2160p|4k)\b",
        r"\b(x264|x265|h264|h265|hevc)\b",
        r"\b(bluray|web[-_. ]?dl|webrip|hdr)\b"
    ]

    for p in patterns:
        name = re.sub(p, "", name, flags=re.IGNORECASE)

    name = re.sub(r"[._\-]+", " ", name)
    return name.strip()


# Work with TVDB API

def get_tvdb_token() -> str:
    response = requests.post(
        TVDB_LOGIN_URL,
        json={"apikey": TVDB_API_KEY},
        timeout=10
    )
    response.raise_for_status()
    return response.json()["data"]["token"]


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


# Fuzzy matching to tv show to allow for flexibility

def score_match(query: str, candidate: dict) -> int:
    title = candidate.get("name", "")
    aliases = candidate.get("aliases", []) or []

    scores = [
        fuzz.token_sort_ratio(query, title),
        fuzz.partial_ratio(query, title)
    ]

    for alias in aliases:
        scores.append(fuzz.token_sort_ratio(query, alias))

    return max(scores)


def pick_best_match(query: str, results: list):
    scored = [(score_match(query, r), r) for r in results]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0] if scored else None


# Scan what seasons exist for each show. 

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


# Scan each show for completeness

def scan_show(show_path: str, token: str):
    cleaned_name = clean_folder_name(show_path)
    results = search_tv_show(cleaned_name, token)

    if not results:
        print(f"\n❓ {cleaned_name}: No TVDB match found")
        return

    best_score, best_match = pick_best_match(cleaned_name, results)

    if best_score < 70:
        print(f"\n  {cleaned_name}: Low confidence match ({best_score})")
        return

    tvdb_id = best_match["tvdb_id"]
    tvdb_seasons = get_tvdb_seasons(tvdb_id, token)
    local_seasons = get_local_seasons(show_path)

    missing = sorted(tvdb_seasons - local_seasons)
    extra = sorted(local_seasons - tvdb_seasons)

    print("\n" + "=" * 60)
    print(f"Show        : {best_match.get('name')}")
    print(f"Folder      : {os.path.basename(show_path)}")
    print(f"TVDB ID     : {tvdb_id}")
    print(f"Score       : {best_score}")
    print(f"TVDB Seasons: {sorted(tvdb_seasons)}")
    print(f"Local       : {sorted(local_seasons)}")

    if missing:
        print(f" Missing  : {missing}")
    else:
        print(" Complete")

    if extra:
        print(f"  Extra    : {extra}")
    
    return (best_match,missing)


# -------------------- LIBRARY SCAN --------------------

def scan_library(root_path: str):
    token = get_tvdb_token()

    print(f"\nScanning TV library: {root_path}")

    for entry in sorted(os.listdir(root_path)):
        show_path = os.path.join(root_path, entry)
        if os.path.isdir(show_path):
            try:
                scan_show(show_path, token)
            except Exception as e:
                print(f"\n💥 Error scanning {entry}: {e}")


# -------------------- MAIN --------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python scan_tv_library_tvdb.py <tv_library_root>")
        sys.exit(1)

    scan_library(sys.argv[1])
