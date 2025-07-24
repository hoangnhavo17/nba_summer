from bs4 import BeautifulSoup
import json
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def try_parse(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

with open("../data/matches.json", "r") as f:
    matches = json.load(f)

all_boxscores = dict()

for game_id, game in matches.items():
    url = game["boxscore_link"]
    print(f"Fetching stats for {game_id}...")

    driver.get(url)
    time.sleep(3)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    tables = soup.select("section.GameBoxscore_gbTableSection__zTOUg")

    game_stats = dict()
    for table in tables:
        team_name = table.select_one("h2.GameBoxscoreTeamHeader_gbt__b9B6g div")
        if not team_name:
            continue
        team_name = team_name.text.strip()

        headers = [th.get_text(strip=True) for th in table.select("thead tr th")]
        
        rows = table.select("tbody tr")
        team_stats = dict()

        for row in rows:
            cells = row.find_all("td")

            if len(cells) != len(headers):
                player = cells[0].get_text(strip=True)
                continue

            raw_name = cells[0].get_text(strip=True)
            name_parts = re.findall(r'[A-Z]\.\s?[A-Za-z-]+', raw_name)
            player_name = name_parts[-1] if len(name_parts) > 1 else raw_name

            role_flag = raw_name[-1]
            starter_roles = {'G', 'F', 'C'}
            is_starter = role_flag in starter_roles

            stats = dict()

            for i, (header, cell) in enumerate(zip(headers, cells)):
                val = cell.get_text(strip=True)
                stats[header] = try_parse(val)

            team_stats[player_name] = stats

        game_stats[team_name] = team_stats

    all_boxscores[game_id] = game_stats

with open("../data/boxscores.json", "w") as f:
    json.dump(all_boxscores, f, indent = 4, ensure_ascii=False)

driver.quit()
