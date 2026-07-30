#!/usr/bin/env python3
"""Validate quiz rounds.

Checks, for every rounds/round-*.json:
  - the file is well-formed and carries the expected top-level fields;
  - every question has a non-empty source URL;
  - no two questions in the same round share a source, compared on
    hostname + path (query strings and anchors ignored);
  - side / category values are from the allowed sets.

Also checks that rounds/index.json is consistent with the round files.

Exit code 0 = all good, 1 = at least one problem. No dependencies.

Usage:  python3 scripts/check.py
"""

import glob
import json
import os
import sys
from urllib.parse import urlsplit

CATEGORIES = {
    "History",
    "Food & drink",
    "Geography",
    "Culture & the arts",
    "Sport & games",
    "Language & everyday life",
    "UK pop & rock",
    "Inventions",
    "Art history",
    "General knowledge",
}
SIDES = {"france", "britain", "both", "neutral"}
FORMATS = {"closest", "order", "oddoneout", "thisorthat"}

# From this round number on, every round must contain at least one question
# from EVERY category — the family asked for guaranteed variety. Earlier rounds
# predate the rule and are exempt (they're already played history).
FULL_COVERAGE_FROM = 13

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUNDS_DIR = os.path.join(ROOT, "rounds")


def source_key(url):
    """Normalise a URL to hostname + path for uniqueness comparison."""
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parts.path.rstrip("/").lower()
    return host + path


def check_round(path, errors):
    name = os.path.relpath(path, ROOT)
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        errors.append(f"{name}: could not parse JSON ({exc})")
        return None

    for field in ("id", "number", "title", "written", "questions"):
        if field not in data:
            errors.append(f"{name}: missing top-level field '{field}'")

    questions = data.get("questions", [])
    if not isinstance(questions, list) or not questions:
        errors.append(f"{name}: 'questions' must be a non-empty array")
        return data

    seen = {}
    for i, q in enumerate(questions, start=1):
        where = f"{name} Q{i}"
        for field in ("category", "side", "question", "answer", "source"):
            if not q.get(field):
                errors.append(f"{where}: missing or empty '{field}'")

        cat = q.get("category")
        if cat and cat not in CATEGORIES:
            errors.append(f"{where}: unknown category '{cat}'")

        side = q.get("side")
        if side and side not in SIDES:
            errors.append(f"{where}: side must be one of {sorted(SIDES)}, got '{side}'")

        fmt = q.get("format")
        if fmt is not None and fmt not in FORMATS:
            errors.append(f"{where}: unknown format '{fmt}' (expected one of {sorted(FORMATS)})")

        items = q.get("items")
        if fmt == "order":
            if not isinstance(items, list) or len(items) < 3:
                errors.append(f"{where}: format 'order' needs an 'items' list of at least 3 entries")
            elif any((not isinstance(i, str) or not i.strip()) for i in items):
                errors.append(f"{where}: every 'items' entry must be a non-empty string")
        elif items is not None:
            errors.append(f"{where}: 'items' is only for format 'order'")

        opts = q.get("options")
        n_expected = 2 if fmt == "thisorthat" else 4
        if fmt in ("oddoneout", "thisorthat") and opts is None:
            errors.append(f"{where}: format '{fmt}' requires 'options'")
        if opts is not None:
            if not isinstance(opts, list) or len(opts) != n_expected:
                errors.append(
                    f"{where}: 'options' must be a list of exactly {n_expected} choices"
                    + (" for this format" if fmt else "")
                )
            elif any((not isinstance(o, str) or not o.strip()) for o in opts):
                errors.append(f"{where}: every option must be a non-empty string")
            else:
                onorm = {o.strip().lower() for o in opts}
                acc = {str(q.get("answer", "")).strip().lower()}
                acc |= {str(a).strip().lower() for a in (q.get("accept") or [])}
                if not (onorm & acc):
                    errors.append(f"{where}: no option matches the answer/accept values")

        for mkey in ("image", "audio", "youtube", "imageCredit", "imageAlt"):
            mv = q.get(mkey)
            if mv is not None and (not isinstance(mv, str) or not mv.strip()):
                errors.append(f"{where}: '{mkey}' must be a non-empty string")

        src = q.get("source")
        if src:
            if not src.strip().lower().startswith(("http://", "https://")):
                errors.append(f"{where}: source is not an http(s) URL: {src!r}")
            else:
                key = source_key(src)
                if key in seen:
                    errors.append(
                        f"{where}: source collides with Q{seen[key]} on host+path "
                        f"({key}) -> {src}"
                    )
                else:
                    seen[key] = i

    # Every category represented? (rounds from FULL_COVERAGE_FROM onwards)
    number = data.get("number")
    if isinstance(number, int) and number >= FULL_COVERAGE_FROM:
        present = {q.get("category") for q in questions if isinstance(q, dict)}
        missing = sorted(CATEGORIES - present)
        if missing:
            errors.append(
                f"{name}: round {number} is missing {len(missing)} categor"
                + ("y" if len(missing) == 1 else "ies")
                + " — every category must appear at least once: "
                + ", ".join(missing)
            )
    return data


def check_index(rounds, errors):
    index_path = os.path.join(ROUNDS_DIR, "index.json")
    if not os.path.exists(index_path):
        errors.append("rounds/index.json is missing")
        return
    try:
        with open(index_path, encoding="utf-8") as fh:
            index = json.load(fh)
    except (OSError, ValueError) as exc:
        errors.append(f"rounds/index.json: could not parse ({exc})")
        return

    if not isinstance(index, list):
        errors.append("rounds/index.json must be an array")
        return

    numbers = [e.get("number") for e in index if isinstance(e, dict)]
    if numbers != sorted(numbers, reverse=True):
        errors.append("rounds/index.json is not sorted newest-first by number")

    by_number = {r["number"]: r for r in rounds if r and "number" in r}
    for entry in index:
        n = entry.get("number")
        rnd = by_number.get(n)
        if rnd is None:
            errors.append(f"rounds/index.json references round {n} with no file")
            continue
        real_count = len(rnd.get("questions", []))
        if entry.get("count") != real_count:
            errors.append(
                f"rounds/index.json round {n}: count {entry.get('count')} "
                f"!= actual {real_count}"
            )
    for n in by_number:
        if n not in numbers:
            errors.append(f"round {n} exists on disk but is missing from index.json")


def main():
    errors = []
    paths = sorted(glob.glob(os.path.join(ROUNDS_DIR, "round-*.json")))
    if not paths:
        print("No rounds found (rounds/round-*.json). Nothing to check.")
        return 0

    rounds = []
    for path in paths:
        rounds.append(check_round(path, errors))

    check_index(rounds, errors)

    if errors:
        print("FAILED — %d problem(s):\n" % len(errors))
        for e in errors:
            print("  - " + e)
        return 1

    total = sum(len(r.get("questions", [])) for r in rounds if r)
    print("OK — %d round(s), %d question(s), all sources unique within each round."
          % (len(paths), total))

    for r in sorted((r for r in rounds if r), key=lambda x: x.get("number", 0)):
        n = r.get("number")
        present = {q.get("category") for q in r.get("questions", [])}
        missing = sorted(CATEGORIES - present)
        if not missing:
            note = "all %d categories" % len(CATEGORIES)
        elif isinstance(n, int) and n < FULL_COVERAGE_FROM:
            note = "%d/%d categories (legacy round, exempt)" % (
                len(CATEGORIES) - len(missing), len(CATEGORIES))
        else:
            note = "MISSING: " + ", ".join(missing)
        print("   round %-3s %3d Q  ·  %s" % (n, len(r.get("questions", [])), note))
    return 0


if __name__ == "__main__":
    sys.exit(main())
