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
                    "starter": stats['STARTER'],
                    "games_played": 0,
                    "game_ids": list(),
                    "total_seconds": 0,
                    "total_stats": defaultdict(int)
                }

            player_summary[player_abbr]["games_played"] += 1
            player_summary[player_abbr]["game_ids"].append(game_id)

            for stat, value in stats.items():
                if stat == "MIN":
                    seconds = parse_min(value)
                    player_summary[player_abbr]["total_seconds"] += seconds
                if isinstance(value, (int, float)) and stat not in ["PLAYER", "MIN", "FG%", "3P%", "FT%"]:
                    player_summary[player_abbr]["total_stats"][stat] += value

final_summary = dict()
for player_abbr, data in player_summary.items():
    games = data["games_played"]
    total_seconds = data["total_seconds"]
    avg_seconds = total_seconds / games if games > 0 else 0
    stats = data["total_stats"]

    total_min_str = format_sec(total_seconds)
    avg_min_str = format_sec(avg_seconds)

    total_stats = {"MIN": total_min_str}
    avg_stats = {"MIN": avg_min_str}

    fgm = stats["FGM"]
    fga = stats["FGA"]
    tpm = stats["3PM"]
    tpa = stats["3PA"]
    ftm = stats["FTM"]
    fta = stats["FTA"]

    def smart_round(value, decimals=1):
        result = round(value, decimals)
        return int(result) if result.is_integer() else result

    totals = {
        "FGM": int(fgm),
        "FGA": int(fga),
        "FG%": smart_round((fgm / fga) * 100) if fga > 0 else 0.0,
        "3PM": int(tpm),
        "3PA": int(tpa),
        "3P%": smart_round((tpm / tpa) * 100) if tpa > 0 else 0.0,
        "FTM": int(ftm),
        "FTA": int(fta),
        "FT%": smart_round((ftm / fta) * 100) if fta > 0 else 0.0,
        "OREB": stats["OREB"],
        "DREB": stats["DREB"],
        "REB": stats["REB"],
        "AST": stats["AST"],
        "STL": stats["STL"],
        "BLK": stats["BLK"],
        "TO": stats["TO"],
        "PF": stats["PF"],
        "PTS": stats["PTS"],
        "+/-": stats["+/-"]
    }

    total_stats.update(totals)

    avgs = {
        "FGM": smart_round(fgm / games) if games > 0 else 0,
        "FGA": smart_round(fga / games) if games > 0 else 0,
        "FG%": total_stats["FG%"],
        "3PM": smart_round(tpm / games) if games > 0 else 0,
        "3PA": smart_round(tpa / games) if games > 0 else 0,
        "3P%": total_stats["3P%"],
        "FTM": smart_round(ftm / games) if games > 0 else 0,
        "FTA": smart_round(fta / games) if games > 0 else 0,
        "FT%": total_stats["FT%"],
        "OREB": smart_round(stats["OREB"] / games) if games > 0 else 0,
        "DREB": smart_round(stats["DREB"] / games) if games > 0 else 0,
        "REB": smart_round(stats["REB"] / games) if games > 0 else 0,
        "AST": smart_round(stats["AST"] / games) if games > 0 else 0,
        "STL": smart_round(stats["STL"] / games) if games > 0 else 0,
        "BLK": smart_round(stats["BLK"] / games) if games > 0 else 0,
        "TO": smart_round(stats["TO"] / games) if games > 0 else 0,
        "PF": smart_round(stats["PF"] / games) if games > 0 else 0,
        "PTS": smart_round(stats["PTS"] / games) if games > 0 else 0,
        "+/-": smart_round(stats["+/-"] / games) if games > 0 else 0
    }

    avg_stats.update(avgs)

    summary = {
        "full_name": data["full_name"],
        "team": data["team"],
        "starter": data["starter"],
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
    response = requests.get(url, timeout=10)
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