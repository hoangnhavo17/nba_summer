from bs4 import BeautifulSoup
from collections import defaultdict
import json
import requests
import time


with open("../data/boxscores.json", "r", encoding="utf-8") as f:
    boxscores = json.load(f)

def parse_min(min_str):
    if isinstance(min_str, str) and ":" in min_str:
        mins, secs = map(int, min_str.split(":"))
        return mins * 60 + secs
    try:
        return int(float(min_str) * 60)
    except:
        return 0.0
    
def format_sec(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"

player_summary = dict()

for game_id, teams in boxscores.items():
    for team_name, players in teams.items():
        for player_abbr, stats in players.items():
            if player_abbr not in player_summary:
                player_summary[player_abbr] = {
                    "full_name": stats['PLAYER'],
                    "team": team_name,
                    "games_played": 0,
                    "game_ids": list(),
                    "total_stats": defaultdict(int)
                }

            player_summary[player_abbr]["games_played"] += 1
            player_summary[player_abbr]["game_ids"].append(game_id)

            for stat, value in stats.items():
                if stat == "MIN":
                    seconds = parse_min(value)
                    player_summary[player_abbr]["total_stats"]["MIN"] += seconds
                if isinstance(value, (int, float)):
                    player_summary[player_abbr]["total_stats"][stat] += value

final_summary = dict()
for player_abbr, data in player_summary.items():
    games = data["games_played"]
    stats = dict(data["total_stats"])

    total_min_str = format_sec(data["total_stats"]["MIN"])
    avg_min_str = format_sec(data["total_stats"]["MIN"] / games) if games > 0 else "0:00"

    total_stats = {"MIN": total_min_str}
    avg_stats = {"MIN": avg_min_str}

    for stat, value in stats.items():
        total_stats[stat] = value
        avg_stats[stat] = value / games if games > 0 else 0

    summary = {
        "full_name": data["full_name"],
        "team": data["team"],
        "position": "Unknown",
        "games_played": data["games_played"],
        "game_ids": data["game_ids"],
        "total_stats": total_stats,
        "avg_stats": avg_stats
    }

    final_summary[player_abbr] = summary

position_map = {
    "point guard": "PG",
    "shooting guard": "SG",
    "small forward": "SF",
    "power forward": "PF",
    "center": "C"
}

def search(query):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
    }
    response = requests.get(url, params=params)
    time.sleep(1)
    data = response.json()
    
    if data["query"]["search"]:
        title = data["query"]["search"][0]["title"]
        return f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}"
    return None

def get_position(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    infobox = soup.find("table", {"class": "infobox"})
    if not infobox:
        return None
    
    position_row = infobox.find("th", string="Position")
    if position_row:
        position_cell = position_row.find_next_sibling("td")
        if position_cell:
            position_links = position_cell.find_all("a")
            positions = [link.text.strip().lower() for link in position_links if link.text.strip().lower()]
            
            return positions if positions else position_cell.text.strip().lower()
    
    return None

def normalize_position(position):
    if isinstance(position, list):
        abbreviations = [position_map.get(p.lower(), p.upper()) for p in position]
        return abbreviations if len(abbreviations) > 1 else abbreviations[0]
    
    elif isinstance(position, str):
        parts = [p.strip().lower() for p in position.split("/") if p.strip()]
        abbreviations = [position_map.get(p, p.upper()) for p in parts]
        return abbreviations if len(abbreviations) > 1 else abbreviations[0]
    
    return "Unknown"

for player_abbr, data in final_summary.items():
    query = f"{data['full_name']}"
    url = search(query)
    if url:
        position = get_position(url)
        position = normalize_position(position)
        if position:
            final_summary[player_abbr]["position"] = position
        else:
            final_summary[player_abbr]["position"] = "Unknown"

with open("../data/players.json", "w", encoding='utf-8') as f:
    json.dump(final_summary, f, indent=4, ensure_ascii=False)