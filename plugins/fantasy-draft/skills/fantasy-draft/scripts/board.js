// Snippets for javascript_tool in the Yahoo draft client (basketball.fantasysports.yahoo.com/draftclient/...).
// Paste one snippet's body as the `text` argument. Results over ~2 KB are truncated: keep slices small.

// --- recorder: log every pick into window.__picks (run once per draft tab) ---
window.__picks = window.__picks || [];
if (!window.__pickTimer) {
  let last = '';
  window.__pickTimer = setInterval(() => {
    const t = document.body.innerText.slice(0, 300).replace(/\n/g, ' | ');
    const m = t.match(/Last: \| (.+?) \| \((.+?)\) \| (.+?) \|/);
    if (m && m[1] !== last) { last = m[1]; window.__picks.push({ at: Date.now(), player: m[1], pos: m[2], by: m[3] }); }
  }, 2000);
}
'recorder on, picks logged: ' + window.__picks.length;

// --- state: banner, the user's roster, top available (Players tab; adjust slice for more rows) ---
const txt = document.body.innerText;
txt.slice(0, 140).replace(/\n/g, ' | ') +
  '\nTEAM: ' + txt.slice(txt.indexOf('YOUR TEAM')).slice(0, 300).replace(/\n/g, ' | ') +
  '\n' + [...document.querySelectorAll('tr')]
    .map(tr => [...tr.querySelectorAll('td')].map(td => td.innerText.trim().replace(/\s+/g, ' ')))
    .filter(r => r.length > 10).slice(0, 20)
    // columns: 0 queue, 1 player, 2 XRank, 3 Rank (Yahoo 9-cat proj), 4 ADP, 5 GP, 6 FG%, 7 FT%, 8 3PTM, 9 PTS, 10 REB, 11 AST, 12 ST, 13 BLK, 14 TO
    .map(r => r[1].slice(0, 24) + ' r' + r[3] + ' a' + r[4] + ' fg' + r[6] + ' ft' + r[7] + ' 3' + r[8] + ' pts' + r[9] + ' reb' + r[10] + ' ast' + r[11] + ' stl' + r[12] + ' blk' + r[13] + ' to' + r[14])
    .join(' ; ');

// --- recent picks from the recorder ---
(window.__picks || []).slice(-14).map(p => p.player + ' (' + p.by + ')').join(', ');

// --- any table (e.g. the Standings tab: projected team category totals) ---
[...document.querySelectorAll('table')].map(tb => [...tb.querySelectorAll('tr')].slice(0, 16)
  .map(tr => [...tr.querySelectorAll('th,td')].map(c => c.innerText.trim().replace(/\s+/g, ' ')).join('|')).join('\n')).join('\n---\n').slice(0, 2000);
