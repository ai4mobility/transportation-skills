"""The D7 signal SOP's numeric rules, written as code.

A model should never do these in its head: a clock time six hours later, a 24-hour
deadline, a $5,000 threshold, a quarter-mile grouping. Each function returns its
answer plus the clause it comes from, so the action card can cite it.

Command line (run from the skill folder):
  python3 scripts/rules.py atms green|yellow|red
  python3 scripts/rules.py refuel "2026-10-10 06:10"
  python3 scripts/rules.py sat "2026-10-10 07:30" "2026-10-11 07:30"
  python3 scripts/rules.py notice "2026-10-08 20:00" "2026-10-09 01:00"
  python3 scripts/rules.py encumber "2026-10-20 15:00"
  python3 scripts/rules.py two 2026-10-20 2026-11-08 --soe yes --funding yes
  python3 scripts/rules.py cost 4800
  python3 scripts/rules.py ddir repairs.csv
repairs.csv columns: repair_id, object_id, lat, lon, cost, kind (emergency|permanent)
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from datetime import date, datetime, timedelta

FMT = "%Y-%m-%d %H:%M"
QUARTER_MILE_M = 0.25 * 1609.344  # 402.336 m
DDIR_THRESHOLD = 5000.0


def _dt(s: str) -> datetime:
    return datetime.strptime(s, FMT)


def atms_status(color: str) -> dict:
    """ATMS symbol color -> signal state (Post-Storm > Immediately Post Storm > 1.1, 1.2)."""
    table = {
        "green": ("operational: actively communicating", "Post-Storm > Immediately Post Storm > 1.1.1",
                  "reflect in eSTORM (1.1.2)"),
        "yellow": ("in flash", "Post-Storm > Immediately Post Storm > 1.2",
                   "evaluate; use to prioritize SAT and generators (1.2.1)"),
        "red": ("non-operational", "Post-Storm > Immediately Post Storm > 1.2",
                "evaluate; use to prioritize SAT and generators (1.2.1)"),
    }
    c = color.strip().lower()
    if c not in table:
        return {"error": f"unknown ATMS color {color!r}; expected green, yellow or red"}
    state, clause, next_step = table[c]
    return {"color": c, "state": state, "next": next_step, "clause": clause}


def first_refuel(deployed_at: str) -> dict:
    """First refueling six hours after initial deployment (Immediately Post Storm > 3.2.1).
    Later refuels follow fueling needs (3.2): a person sets those."""
    t = _dt(deployed_at) + timedelta(hours=6)
    return {"deployed": deployed_at, "first_refuel": t.strftime(FMT),
            "clause": "Post-Storm > Immediately Post Storm > 3.2.1",
            "after_that": "schedule based on fueling needs (3.2): a person decides"}


def sat_passes(start: str, end: str) -> dict:
    """SAT assessments at 9:00 AM and 2:00 PM daily (Immediately Post Storm > 6.1;
    0-1 Week Post Storm > 1)."""
    t0, t1 = _dt(start), _dt(end)
    out = []
    d = t0.date()
    while d <= t1.date():
        for hh in (9, 14):
            t = datetime(d.year, d.month, d.day, hh, 0)
            if t0 <= t <= t1:
                out.append(t.strftime(FMT))
        d += timedelta(days=1)
    return {"passes": out, "clause": "Post-Storm > 0-1 Week Post Storm > 1"}


def crew_notice_ok(notified_at: str, deploy_at: str) -> dict:
    """At least 6-hour notice for all crews (Pre-Storm > 24 Hours Prior > 1)."""
    hours = (_dt(deploy_at) - _dt(notified_at)).total_seconds() / 3600
    return {"notice_hours": round(hours, 2), "ok": hours >= 6,
            "clause": "Pre-Storm > 24 Hours Prior > 1"}


def encumber_by(two_issued_at: str) -> dict:
    """Encumber funds in CFM within 24 hours (TWO > Emergency TWOs > 9)."""
    return {"two_issued": two_issued_at,
            "encumber_by": (_dt(two_issued_at) + timedelta(hours=24)).strftime(FMT),
            "clause": "TWO > Emergency TWOs > 9"}


def emergency_two_allowed(issue: str, eo_expires: str, soe: bool, funding: bool) -> dict:
    """TWO > Emergency TWOs > 1 (State of Emergency ordered, funding programmed) and
    > 12 (not after the governor's executive order expires)."""
    reasons = []
    if not soe:
        reasons.append("no State of Emergency ordered (TWO 1)")
    if not funding:
        reasons.append("funding not programmed or appropriated (TWO 1)")
    if date.fromisoformat(issue) > date.fromisoformat(eo_expires):
        reasons.append("executive order has expired (TWO 12)")
    note = None
    if date.fromisoformat(issue) == date.fromisoformat(eo_expires):
        note = "issue date equals the EO expiry date: confirm the exact expiry time with a person"
    return {"allowed": not reasons, "blocked_by": reasons, "note": note,
            "clauses": ["TWO > Emergency TWOs > 1", "TWO > Emergency TWOs > 12"]}


def cost_bucket(cost: float) -> dict:
    """< $5,000 or => $5,000 (0-1 Week Post Storm > 6.1.1)."""
    return {"cost": cost, "bucket": ">= $5,000" if cost >= DDIR_THRESHOLD else "< $5,000",
            "clause": "Post-Storm > 0-1 Week Post Storm > 6.1.1"}


def _meters(a: dict, b: dict) -> float:
    r = 6371008.8
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp, dl = p2 - p1, math.radians(b["lon"] - a["lon"])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def ddir_candidates(repairs: list[dict]) -> dict:
    """Propose DDIR groups: same Object ID, or chained within 1/4 mile
    (Funding > 0-1 Month Post Storm > 1 and 2.1). The DDIR team decides the final
    grouping (TWO > Emergency TWOs > 4), so this is a proposal, not a decision.

    The SOP says ">= $5,000" in 0-1 Month 1 and 0-1 Week 6.1.1 but "exceeds $5,000"
    in 0-1 Month 2.1. A group whose total is exactly $5,000 is flagged for a person."""
    n = len(repairs)
    parent = list(range(n))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(n):
        for j in range(i + 1, n):
            same_obj = repairs[i]["object_id"] == repairs[j]["object_id"]
            if same_obj or _meters(repairs[i], repairs[j]) <= QUARTER_MILE_M:
                parent[find(i)] = find(j)
    groups: dict[int, list[dict]] = {}
    for i, r in enumerate(repairs):
        groups.setdefault(find(i), []).append(r)
    out = []
    for members in groups.values():
        total = sum(m["cost"] for m in members)
        emer = sum(m["cost"] for m in members if m["kind"] == "emergency")
        perm = total - emer
        span = max((_meters(a, b) for a in members for b in members), default=0.0)
        flags = []
        if total == DDIR_THRESHOLD:
            flags.append("total is exactly $5,000: 0-1 Month 1 says '$5000 or greater', "
                         "2.1 says 'exceeds $5,000'. Ask the DDIR team.")
        if span > QUARTER_MILE_M:
            flags.append(f"chained group spans {span:.0f} m (> 1/4 mile end to end). "
                         "Ask the DDIR team whether to split it.")
        out.append({
            "repairs": [m["repair_id"] for m in members],
            "objects": sorted({m["object_id"] for m in members}),
            "total": total, "emergency": emer, "permanent": perm,
            "needs_ddir": total >= DDIR_THRESHOLD,
            "flags": flags,
        })
    out.sort(key=lambda g: -g["total"])
    return {"groups": out,
            "clauses": ["Funding > 0-1 Month Post Storm > 1", "Funding > 0-1 Month Post Storm > 2.1",
                        "TWO > Emergency TWOs > 4"],
            "decided_by": "DDIR team (TWO > Emergency TWOs > 4)"}


def read_repairs(path: str) -> list[dict]:
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["lat"], r["lon"], r["cost"] = float(r["lat"]), float(r["lon"]), float(r["cost"])
        r["kind"] = r["kind"].strip().lower()
    return rows


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("atms").add_argument("color")
    sub.add_parser("refuel").add_argument("deployed_at")
    p = sub.add_parser("sat"); p.add_argument("start"); p.add_argument("end")
    p = sub.add_parser("notice"); p.add_argument("notified_at"); p.add_argument("deploy_at")
    sub.add_parser("encumber").add_argument("two_issued_at")
    p = sub.add_parser("two"); p.add_argument("issue"); p.add_argument("eo_expires")
    p.add_argument("--soe", default="yes"); p.add_argument("--funding", default="yes")
    sub.add_parser("cost").add_argument("cost", type=float)
    sub.add_parser("ddir").add_argument("csv")
    a = ap.parse_args()
    if a.cmd == "atms":
        r = atms_status(a.color)
    elif a.cmd == "refuel":
        r = first_refuel(a.deployed_at)
    elif a.cmd == "sat":
        r = sat_passes(a.start, a.end)
    elif a.cmd == "notice":
        r = crew_notice_ok(a.notified_at, a.deploy_at)
    elif a.cmd == "encumber":
        r = encumber_by(a.two_issued_at)
    elif a.cmd == "two":
        r = emergency_two_allowed(a.issue, a.eo_expires, a.soe == "yes", a.funding == "yes")
    elif a.cmd == "cost":
        r = cost_bucket(a.cost)
    else:
        r = ddir_candidates(read_repairs(a.csv))
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    main()
