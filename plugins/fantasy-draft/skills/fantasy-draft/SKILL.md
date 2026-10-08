---
name: fantasy-draft
description: Live pick advisor for Yahoo Fantasy Basketball drafts (9-cat H2H). Reads the Yahoo draft room in the user's Chrome (Claude in Chrome), records every pick, tracks their roster and category balance, and suggests the next pick when they're on the clock. Pulls extra NBA data from nba-api.xyz when needed. Use when the user is in a draft or mock draft, shares a Yahoo draftclient / mock_waiting URL, says "my turn" / "up" / "up in N", or asks who to draft.
---

# Fantasy draft advisor (Yahoo, 9-cat H2H)

The draft is on Yahoo. Yahoo's Fantasy API needs a manual app approval, so the draft room is read from the user's Chrome with the Claude in Chrome tools (the user must be logged in to Yahoo there). **Read only: never click Draft, never star or queue players, never touch their Yahoo settings.** For data the draft room doesn't show (game logs, last season's stats, schedules), use https://nba-api.xyz: its `/api/...` JSON routes (listed at https://nba-api.xyz/docs) or the `/stats/<endpoint>?...` passthrough to stats.nba.com (cached and rate-limited, no key).

## Goal and strategy

- Format: head-to-head 9-cat (FG%, FT%, 3PTM, PTS, REB, AST, ST, BLK, TO). Winning 5 of 9 wins the week, so build a team that is strong in 5-6 categories instead of average in all 9. Decide whether to punt (FT%, TO, AST and BLK are the usual candidates) after 2-3 picks, from what the roster is becoming, not up front.
- Value source: Yahoo's own **2026-27 projections** in the draft room (the `Rank` column is Yahoo's projected 9-cat rank; `ADP` is where players usually go). Those already include returning stars (Tatum, Haliburton, Dame…), trades and rookies. Prefer them over last season's stats. `${CLAUDE_SKILL_DIR}/scripts/zscore.py` is the fallback when the room isn't readable.
- Positional market: guards and wings go early; blocking centers run deep (Kessler, Clingan, Ware, Sarr, Gobert, Turner, Missi lasted into rounds 3-8 of a 14-team mock). Take value wings early, get bigs in the middle rounds, and use guards' FT% to absorb a bad-FT center.
- Skip players whose one category destroys you unless you punt it (Giannis: projected 50th in 9-cat because of FT%).

## Setup (once per draft)

1. Load the browser tools in one ToolSearch call (`tabs_context_mcp`, `tabs_create_mcp`, `navigate`, `computer`, `javascript_tool`, `get_page_text`, `find`, `tabs_close_mcp`).
2. Open the URL the user gives (waiting room or `draftclient`) in a **new tab** of the MCP group. The waiting room shows league settings: number of teams, the user's draft slot, roster slots, categories. The draft client opens in the same tab when the draft starts.
3. Compute the user's pick numbers (snake): `python3 ${CLAUDE_SKILL_DIR}/scripts/picks.py <teams> <slot> <rounds>`.
4. Install the pick recorder (the "recorder" snippet in `${CLAUDE_SKILL_DIR}/scripts/board.js`) with `javascript_tool`. It logs every pick into `window.__picks` every 2 s, so one read later gives the whole history. Don't run a polling loop on your side: it would block the chat. The user says "up" / "my turn" / "up in N", and you read the board then.

## Every time the user asks (or says "up")

1. **Re-read the board first, every time.** Never suggest from memory: players vanish between turns (a mock suggested Cason Wallace after he was gone). Run the "state" snippet from `${CLAUDE_SKILL_DIR}/scripts/board.js`: the banner (whose pick, picks until the user), the user's roster panel, and the top available players with Rank, ADP and stats. Results over ~2 KB are truncated, so read in slices of ~20 rows.
2. Work out the roster's category profile from their players' projections: which categories are locked, which are close, which are lost or punted, and which roster slots are still empty (PG, SG, G, SF, PF, F, C, C, Util, Util).
3. Answer fast (assume a 60 s pick clock; the banner shows the real countdown, e.g. `00:22`): **one pick in bold first**, one line of why (categories plus slot), then 2-3 fallbacks in order. When they're "up in N", give an ordered shortlist that survives a few picks.
4. Use names exactly as Yahoo shows them (`D. Peterson`, `C. Wilson`). **Never expand a first name you aren't sure of.** Say "D. Peterson (SG, UTA)".
5. After their pick, note the roster and the next pick number, and pre-plan the shortlist.

## Files

- `scripts/board.js`: the JS snippets (recorder, state, rows, standings) to paste into `javascript_tool`.
- `scripts/picks.py`: snake pick numbers.
- `${CLAUDE_SKILL_DIR}/scripts/zscore.py`: fallback 9-cat z-scores from nba-api.xyz (`python3 ${CLAUDE_SKILL_DIR}/scripts/zscore.py 2025-26 2024-25 <teams>`), with returning players from the prior season discounted for injury.
