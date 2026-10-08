#!/usr/bin/env python3
"""Fallback 9-cat values when the Yahoo draft room can't be read.

zscore.py <season> <prev-season> <teams> [roster]   e.g.  zscore.py 2025-26 2024-25 14 13

Fetches per-game stats for both seasons from nba-api.xyz (no install or key needed),
adds players who missed most of <season> but played 40+ games at 25+ min in
<prev-season> (their prev line discounted for recovery), and prints players ranked by
summed z-scores over PTS REB AST STL BLK 3PM TO FG% FT% (FG%/FT% weighted by attempts),
with the pool sized to teams*roster and refined three times.
"""
import json, statistics as st, sys, urllib.parse, urllib.request

season, prev, teams = sys.argv[1], sys.argv[2], int(sys.argv[3])
roster = int(sys.argv[4]) if len(sys.argv) > 4 else 13
# Recovery discounts for notable returners (edit per season); everyone else 0.93.
DISC = {"Damian Lillard": 0.88, "Kyrie Irving": 0.90, "Jayson Tatum": 0.95, "Tyrese Haliburton": 0.95}
CATS = ["PTS", "REB", "AST", "STL", "BLK", "FG3M", "TOV", "FGp", "FTp"]


def dash(s):
    """Per-game stats for a season from nba-api.xyz (a public, cached NBA stats proxy)."""
    q = urllib.parse.urlencode({
        "LastNGames": 0, "LeagueID": "00", "MeasureType": "Base", "Month": 0, "OpponentTeamID": 0,
        "PaceAdjust": "N", "PerMode": "PerGame", "Period": 0, "PlusMinus": "N", "Rank": "N",
        "Season": s, "SeasonType": "Regular Season", "TeamID": 0}, quote_via=urllib.parse.quote)
    req = urllib.request.Request(f"https://nba-api.xyz/stats/leaguedashplayerstats?{q}",
                                 headers={"User-Agent": "fantasy-draft-skill"})
    with urllib.request.urlopen(req, timeout=60) as r:
        body = json.load(r)
    rs = body["resultSets"][0]
    return [dict(zip(rs["headers"], row)) for row in rs["rowSet"]]


rows, old = dash(season), {r["PLAYER_ID"]: r for r in dash(prev)}
cur = {r["PLAYER_ID"]: r for r in rows}
P = [dict(r, ret=False) for r in rows if (r.get("GP") or 0) >= 20 and (r.get("MIN") or 0) >= 15]
for pid, r in old.items():
    c = cur.get(pid)
    if (c is None or c["GP"] < 20) and r["GP"] >= 40 and r["MIN"] >= 25:
        f = DISC.get(r["PLAYER_NAME"], 0.93)
        q = dict(r, ret=True)
        for k in ["PTS", "REB", "AST", "STL", "BLK", "FG3M", "TOV", "FGM", "FGA", "FTM", "FTA"]:
            q[k] = r[k] * f
        P.append(q)


def build(pool):
    fg = sum(p["FGM"] for p in pool) / sum(p["FGA"] for p in pool)
    ft = sum(p["FTM"] for p in pool) / max(1, sum(p["FTA"] for p in pool))
    for p in P:
        p["FGp"], p["FTp"] = (p["FG_PCT"] - fg) * p["FGA"], (p["FT_PCT"] - ft) * p["FTA"]
    mu = {c: st.mean(p[c] for p in pool) for c in CATS}
    sd = {c: st.pstdev(p[c] for p in pool) for c in CATS}
    for p in P:
        p["z"] = {c: (p[c] - mu[c]) / sd[c] * (-1 if c == "TOV" else 1) for c in CATS}
        p["Z"] = sum(p["z"].values())


pool = P
for _ in range(3):
    build(pool)
    pool = sorted(P, key=lambda p: -p["Z"])[: teams * roster]
build(pool)
for i, p in enumerate(sorted(P, key=lambda p: -p["Z"])[: teams * roster], 1):
    z = p["z"]
    print(f"{i:>3} {'*' if p['ret'] else ' '}{p['PLAYER_NAME'][:22]:22} {p['TEAM_ABBREVIATION']} Z{p['Z']:6.2f} | "
          + " ".join(f"{c[:3]}{z[c]:+.1f}" for c in CATS))
