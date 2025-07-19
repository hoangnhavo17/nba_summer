import json
from nba_api.stats.static import teams

nba_teams = teams.get_teams()

team_map = {
    team['full_name']: {
        'abbreviation': team['abbreviation'],
        'nickname': team['nickname'],
        'city': team['city'],
        'id': team['id']
    }
    for team in nba_teams
}

with open("../data/teams.json", "w") as f:
    json.dump(team_map, f, indent=2)
