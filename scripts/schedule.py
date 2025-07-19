from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import requests
import time

with open("../data/teams.json", "r") as f:
    teams = json.load(f)

city_to_abbr = dict()
for team_name, team_info in teams.items():
    city = team_info['city']
    abbr = team_info['abbreviation']
    
    if abbr == "GSW":
        city_to_abbr["Golden State"] = "GS"
    elif abbr == "LAC":
        city_to_abbr["LA"] = "LAC"
    elif abbr == "NOP":
        city_to_abbr["New Orleans"] = "NO"
    elif abbr == "NYK":
        city_to_abbr["New York"] = "NY"
    elif abbr == "UTA":
        city_to_abbr['Utah'] = "UTAH"
    elif abbr == "WAS":
        city_to_abbr['Washington'] = "WSH"
    else:
        city_to_abbr[city] = abbr

url = "https://en.wikipedia.org/wiki/2025_NBA_Summer_League"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

target_heading = soup.find("h2", id="Las_Vegas_Summer_League")
section_div = target_heading.find_parent("div", class_="mw-heading2")

vegas_games = []
current = section_div.find_next_sibling()
while current and not (current.name == "div" and "mw-heading2" in current.get("class", [])):
    if current.name == "div":
        text = current.get_text(separator="\n").strip()
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        # Skip if structure isn't right
        if len(lines) < 3:  # not enough info
            current = current.find_next_sibling()
            continue

        # Extract date/time
        date_time_line = lines[0]
        match = re.match(r"([A-Za-z]+\s\d+)\s+([0-9:APM]+ PDT)", date_time_line)
        if not match:
            current = current.find_next_sibling()
            continue

        date = match.group(1)
        time = match.group(2)

        # Extract teams line (e.g., "Golden State Warriors vs. Toronto Raptors")
        team_line = next((line for line in lines if "vs." in line), None)

        # Extract score from team_line (after parsing team names if you want)
        # or use Boxscore link later to get box score data if needed

        vegas_games.append({
            "date": date,
            "time": time,
            "matchup": team_line
        })

    current = current.find_next_sibling()

# Print result
for game in vegas_games:
    print(f"{game['date']} {game['time']} - {game['matchup']}")
