import json
import requests

# Load team data
with open("../data/teams.json", "r") as f:
    teams = json.load(f)

# ESPN uses different abbreviations from NBA
abbr_override = {
    "NOP": "NO",
    "UTA": "UTAH"
}

# ESPN logo base url
base_url = "https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/scoreboard/{abbr}.png"

for team_name, team_info in teams.items():
    nba_abbr = team_info['abbreviation'].upper()
    espn_abbr = abbr_override.get(nba_abbr, nba_abbr.lower())
    logo_url = base_url.format(abbr=espn_abbr)

    try:
        response = requests.get(logo_url)
        response.raise_for_status()
        with open(f"../data/logos/{nba_abbr}.png", "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"Failed to download logo for {team_name}: {e}")

    team_info['logo'] = f"../data/logos/{nba_abbr}.png"

with open("../data/teams.json", "w") as f:
    json.dump(teams, f, indent=4)
