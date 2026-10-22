# 🌀 The Hunt Loop — Playbook

Mars runs the same four phases every session. Skipping a phase is how cats fall off counters.

## 01 · PROWL — scan the field
**Goal:** go from thousands of pairs to a handful worth watching.

- Scan new listings and momentum: Dexscreener, GMGN, CoinGecko
- First filters: minimum liquidity, pair age, volume consistency (not one giant candle)
- Explorer check: holder spread, mint/freeze authority, LP locked or burned
- **Output:** a shortlist of ≤ 5 candidates. Most sessions end here — that's fine.

## 02 · STALK — build the thesis
**Goal:** turn a candidate into a plan, or kill it.

- Write the thesis in one sentence
- List 2–4 concrete signals that support it
- Write the **invalidation** first — the price or event that means she's wrong
- Define entry, size (≤ 1% of jar), take-profit zone
- Create the entry: `mars new "<pair> <idea>"`
- **Output:** a diary entry with the "before" half complete.

## 03 · POUNCE — execute cleanly
**Goal:** do exactly what the plan says.

- Enter per plan. If price ran away, she lets it go — there's always another bird.
- `mars log --pair ... --entry ... --size ... --mood ...`
- Hands off. No moving the invalidation, no adding to losers.
- **Output:** a ledger row.

## 04 · GROOM — reflect and improve
**Goal:** extract one lesson per trade.

- Write the outcome in numbers
- Was the thesis right, or did she get lucky? Both happen; be honest about which.
- Did any rule fail? Propose the change, commit it to `docs/rules.md` with a reason
- `mars stats` to see the bigger picture
- **Output:** a complete diary entry, maybe a rule commit, and a nap.

---

### Session checklist
- [ ] Rules re-read (`mars rules`)
- [ ] Prowl shortlist written down
- [ ] Every pounce has a diary entry *before* entry
- [ ] Every trade logged
- [ ] Groom done before closing the laptop
