#!/usr/bin/env python3
"""
mars — the cat trading companion CLI.  =^.^=

Pure standard library. Usage:
    python scripts/mars.py wake
    python scripts/mars.py new "first pounce"
    python scripts/mars.py log --pair EXAMPLE/SOL --side long --entry 0.01 --exit 0.012 --size 1 --mood zoomies
    python scripts/mars.py stats
    python scripts/mars.py rules
    python scripts/mars.py purr
"""
import argparse
import csv
import datetime as dt
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIARY = os.path.join(ROOT, "diary")
LOGS = os.path.join(ROOT, "logs", "trades.csv")
RULES = os.path.join(ROOT, "docs", "rules.md")
README = os.path.join(ROOT, "README.md")
FIELDS = ["id", "date", "pair", "side", "entry", "exit", "size_pct", "pnl_pct", "mood", "note"]
MOODS = ("hiss", "nap", "zoomies")

# ── colours ──────────────────────────────────────────────────────────────
TTY = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None
def c(code, s): return f"\033[{code}m{s}\033[0m" if TTY else s
PINK = lambda s: c("38;5;211", s)
LAV = lambda s: c("38;5;183", s)
MINT = lambda s: c("38;5;121", s)
RED = lambda s: c("38;5;204", s)
DIM = lambda s: c("2", s)
BOLD = lambda s: c("1", s)

BANNER = r"""
   /\_/\      __  __    _    ____  ____
  ( o.o )    |  \/  |  / \  |  _ \/ ___|
   > ^ <     | |\/| | / _ \ | |_) \___ \ 
  /     \    | |  | |/ ___ \|  _ < ___) |
 (_______)   |_|  |_/_/   \_\_| \_\____/
"""


def type_out(s, delay=0.004):
    if not TTY:
        print(s); return
    for ch in s:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()


def ensure_ledger():
    os.makedirs(os.path.dirname(LOGS), exist_ok=True)
    if not os.path.exists(LOGS) or os.path.getsize(LOGS) == 0:
        with open(LOGS, "w", newline="") as f:
            csv.writer(f).writerow(FIELDS)


def read_trades():
    ensure_ledger()
    with open(LOGS, newline="") as f:
        return [r for r in csv.DictReader(f) if r.get("id")]


# ── commands ─────────────────────────────────────────────────────────────
def cmd_wake(_):
    print(PINK(BANNER))
    type_out(LAV("$ mars wake --mode=purr"))
    checks = [
        ("diary/", os.path.isdir(DIARY)),
        ("diary/000_template.md", os.path.exists(os.path.join(DIARY, "000_template.md"))),
        ("docs/rules.md", os.path.exists(RULES)),
        ("logs/trades.csv", True),
    ]
    ensure_ledger()
    for name, ok in checks:
        dots = "." * (34 - len(name))
        type_out(f"  ↳ {name} {DIM(dots)} " + (MINT("ok") if ok else RED("missing")))
    n = len(read_trades())
    type_out(MINT(f"  ✓ eyes open. {n} trade(s) in the ledger."))


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40] or "entry"


def cmd_new(a):
    os.makedirs(DIARY, exist_ok=True)
    nums = [int(m.group(1)) for f in os.listdir(DIARY) if (m := re.match(r"(\d{3})_", f))]
    n = max(nums + [0]) + 1
    path = os.path.join(DIARY, f"{n:03d}_{slug(a.title)}.md")
    tpl = open(os.path.join(DIARY, "000_template.md")).read()
    today = dt.date.today().isoformat()
    body = (tpl.replace("{{NUMBER}}", f"{n:03d}")
               .replace("{{TITLE}}", a.title)
               .replace("{{DATE}}", today))
    with open(path, "w") as f:
        f.write(body)
    print(MINT("✓ ") + f"new diary entry → {os.path.relpath(path, ROOT)}")
    print(DIM("  write THESIS / SIGNALS / INVALIDATION / PLAN before you pounce."))


def cmd_log(a):
    if a.mood not in MOODS:
        sys.exit(RED(f"mood must be one of {MOODS}"))
    trades = read_trades()
    tid = max([int(t["id"]) for t in trades] + [0]) + 1
    pnl = ""
    if a.exit is not None:
        raw = (a.exit - a.entry) / a.entry * 100
        pnl = f"{raw if a.side == 'long' else -raw:.2f}"
    row = {"id": tid, "date": a.date or dt.date.today().isoformat(), "pair": a.pair, "side": a.side,
           "entry": a.entry, "exit": "" if a.exit is None else a.exit, "size_pct": a.size,
           "pnl_pct": pnl, "mood": a.mood, "note": a.note}
    with open(LOGS, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)
    col = MINT if pnl and float(pnl) >= 0 else RED
    print(MINT("✓ ") + f"trade #{tid} logged · {a.pair} {a.side} · " + (col(f"{pnl}%") if pnl else LAV("open")))


def spark(vals):
    bars = "▁▂▃▄▅▆▇█"
    if not vals: return ""
    lo, hi = min(vals), max(vals)
    rng = (hi - lo) or 1
    return "".join(bars[int((v - lo) / rng * (len(bars) - 1))] for v in vals)


def cmd_stats(_):
    trades = [t for t in read_trades() if t["pnl_pct"]]
    print(PINK(BOLD("\n  =^.^=  MARS · HUNT REPORT\n")))
    if not trades:
        print(DIM("  no closed trades yet. the cat is still watching the window.\n")); return
    pnl = [float(t["pnl_pct"]) for t in trades]
    sized = [float(t["pnl_pct"]) * float(t["size_pct"] or 0) / 100 for t in trades]
    wins = [p for p in pnl if p > 0]
    eq, curve = 0.0, []
    for s in sized:
        eq += s; curve.append(eq)
    streak = best_streak = worst_streak = 0
    for p in pnl:
        streak = streak + 1 if (p > 0 and streak >= 0) else (1 if p > 0 else (streak - 1 if streak <= 0 else -1))
        best_streak = max(best_streak, streak); worst_streak = min(worst_streak, streak)
    moods = {m: sum(1 for t in trades if t["mood"] == m) for m in MOODS}
    rows = [
        ("closed trades", str(len(pnl))),
        ("win rate", f"{len(wins) / len(pnl) * 100:.1f}%"),
        ("avg trade", f"{sum(pnl) / len(pnl):+.2f}%"),
        ("best / worst", f"{max(pnl):+.2f}% / {min(pnl):+.2f}%"),
        ("jar impact", f"{eq:+.3f}% of jar"),
        ("streaks", f"{best_streak}W / {-worst_streak}L"),
        ("moods", "  ".join(f"{m}:{n}" for m, n in moods.items())),
    ]
    for k, v in rows:
        print(f"  {LAV(k.ljust(14))} {v}")
    print(f"\n  {LAV('equity'.ljust(14))} {PINK(spark(curve))}\n")


def cmd_rules(_):
    print(open(RULES).read())


def cmd_purr(_):
    for line in ["  /\\_/\\  ", " ( -.- )  purr…", "  > ^ <  ", DIM("  mars is pleased. nothing was traded.")]:
        type_out(PINK(line), 0.02)


def main():
    p = argparse.ArgumentParser(prog="mars", description="the cat trading companion =^.^=")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("wake").set_defaults(fn=cmd_wake)
    n = sub.add_parser("new"); n.add_argument("title"); n.set_defaults(fn=cmd_new)
    l = sub.add_parser("log")
    l.add_argument("--pair", required=True)
    l.add_argument("--side", choices=["long", "short"], default="long")
    l.add_argument("--entry", type=float, required=True)
    l.add_argument("--exit", type=float)
    l.add_argument("--size", type=float, default=1.0, help="%% of jar risked")
    l.add_argument("--mood", default="nap", choices=MOODS)
    l.add_argument("--note", default="")
    l.add_argument("--date")
    l.set_defaults(fn=cmd_log)
    sub.add_parser("stats").set_defaults(fn=cmd_stats)
    sub.add_parser("rules").set_defaults(fn=cmd_rules)
    sub.add_parser("purr").set_defaults(fn=cmd_purr)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
