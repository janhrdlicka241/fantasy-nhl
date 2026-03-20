import requests
import json
from datetime import datetime

BASE = "https://api.nhle.com/stats/rest/en"
SCORE = "https://api-web.nhle.com/v1/score/now"
SEASON = "20242025"

def fetch(url):
    r = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    return r.json()

print("Fetching NHL skater stats...")
skaters_data = fetch(f"{BASE}/skater/summary?limit=500&start=0&sort=points&cayenneExp=seasonId={SEASON}%20and%20gameTypeId=2")

print("Fetching NHL goalie stats...")
goalies_data = fetch(f"{BASE}/goalie/summary?limit=100&start=0&sort=wins&cayenneExp=seasonId={SEASON}%20and%20gameTypeId=2")

print("Fetching today's scoreboard...")
try:
    score_data = fetch(SCORE)
    games = score_data.get("games", [])
except:
    games = []

# Build stats dict
stats = {}

for p in skaters_data.get("data", []):
    pid = str(p.get("playerId", ""))
    if pid:
        stats[pid] = {
            "goals":   p.get("goals", 0),
            "assists": p.get("assists", 0),
            "gp":      p.get("gamesPlayed", 0),
            "points":  p.get("points", 0),
            "shutouts": 0,
            "wins": 0,
        }

for p in goalies_data.get("data", []):
    pid = str(p.get("playerId", ""))
    if pid:
        stats[pid] = {
            "goals":    0,
            "assists":  p.get("assists", 0),
            "gp":       p.get("gamesPlayed", 0),
            "points":   0,
            "shutouts": p.get("shutouts", 0),
            "wins":     p.get("wins", 0),
            "savePct":  round(p.get("savePctg", 0) * 100, 1),
            "gaa":      round(p.get("goalsAgainstAverage", 0), 2),
        }

# Today's games summary
today_games = []
for g in games:
    away = g.get("awayTeam", {})
    home = g.get("homeTeam", {})
    today_games.append({
        "away": away.get("abbrev", "?"),
        "home": home.get("abbrev", "?"),
        "awayScore": away.get("score"),
        "homeScore": home.get("score"),
        "state": g.get("gameState", ""),
    })

output = {
    "updatedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    "season": SEASON,
    "stats": stats,
    "todayGames": today_games,
}

with open("stats.json", "w") as f:
    json.dump(output, f)

print(f"Done! Saved {len(stats)} players, {len(today_games)} games today.")
