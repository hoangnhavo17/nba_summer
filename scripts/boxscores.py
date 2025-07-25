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
    time.sleep(5)

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

            player_span = cells[0].select_one("span.GameBoxscoreTablePlayer_gbpNameFull__cf_sn")
            player_name = player_span.get_text(strip=True) if player_span else cells[0].get_text(strip=True)

            abbr_span = cells[0].select_one("span.GameBoxscoreTablePlayer_gbpNameShort__hjcGB")
            abbr_name = abbr_span.get_text(strip=True) if abbr_span else cells[0].get_text(strip=True)

            starter_tag = cells[0].select_one("span.GameBoxscoreTablePlayer_gbpPos__KW2Nf")
            role_text = starter_tag.get_text(strip=True) if starter_tag else ""
            is_starter = role_text in ["G", "F", "C"]

            stats = dict()

            for header, cell in zip(headers, cells):
                val = cell.get_text(strip=True)
                stats[header] = try_parse(val)

            stats["PLAYER"] = player_name
            team_stats[abbr_name] = stats

        game_stats[team_name] = team_stats

    all_boxscores[game_id] = game_stats

with open("../data/boxscores.json", "w", encoding='utf-8') as f:
    json.dump(all_boxscores, f, indent = 4, ensure_ascii=False)

driver.quit()
