from bs4 import BeautifulSoup
import json
import re
import requests

with open("../data/teams.json", "r") as f:
    teams = json.load(f)

url = "https://en.wikipedia.org/wiki/2025_NBA_Summer_League"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

games_header = soup.find("h3", id="Games_3")

content = list()
current = games_header.find_parent().find_next_sibling()

while current:
    if current.name == "div" and current.find("h2") and "References" in current.text:
        break
    if current.name == "div" and current.get("style", "").startswith("width: 100%"):
        content.append(current)
    current = current.find_next_sibling()

games = dict()

for i, div in enumerate(content):
    tables = div.find_all("table")

    datetime = tables[1].text.strip()

    boxscore = tables[2].find("a")["href"]
    boxscore = f"https://en.wikipedia.org{boxscore}" if boxscore.startswith("/") else boxscore
    
    result = tables[3].find_all("tr")[0].text.strip()

    game = {
        "date": datetime,
        "result": result,
        "boxscore_link": boxscore
    }

    match = re.search(r'(\d{10})', boxscore)
    game_id = match.group(1) if match else None

    games[game_id] = game
    
with open("../data/matches.json", "w") as f:
    json.dump(games, f, indent = 4, ensure_ascii=False)
