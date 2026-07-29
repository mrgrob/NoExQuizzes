---
name: create-quizz-session
description: >-
  Produce one evening's round of questions for the Franco-British family quiz
  in this repo (NoExQuizzes). Load this whenever the user asks for a new quiz
  round or evening session — e.g. "fais la session de ce soir", "new quiz
  round", "quiz for tonight", "prépare le quiz", "another round", or the
  /create-quizz-session command. The procedure researches and verifies every
  question, enforces one unique source per question and per-category quotas,
  writes rounds/round-N.json, regenerates rounds/index.json, commits, pushes,
  and reports the per-category counts and the live URL.
---

# Create a quiz session

You are the generator. There is **no API key** anywhere in this project — not
in the frontend, not in GitHub Secrets, not in a serverless function. When the
user asks for a round, **you** research and write the questions here in the
session, then commit finished JSON. The published site is pure static files
that only ever read local JSON. If you find yourself reaching for an Anthropic
API call, a `.env`, a backend, or a build step, stop — that is the design being
violated, not a missing piece.

Your output is one file, `rounds/round-N.json`, plus a refreshed
`rounds/index.json`. The **quality of the questions is the whole product.**
A round of 27 solid questions beats 30 with one invented citation.

## Parameters (all optional)

The user may specify any of these; use the defaults when they don't.

| Parameter | Default | Notes |
|---|---|---|
| `theme` | none | A loose thread to lean into (e.g. "the sea", "1900", "kings and queens"). Never let a theme override the category quotas or the balance rules. |
| `difficulty` | `pub` | `gentle` = a well-read teenager gets most; `pub` = a reasonably informed adult gets many; `fiendish` = rewards real knowledge, still fair and timeless. |
| `perCategory` | `5` | Questions per category. `5` → 30 total. `perCategory: 6` → 36, etc. |

## The rules that make or break the round

### 1. Verify before writing
Web-search to check **each** fact **before** committing to the question, never
after. Take the source URL from the search result you actually opened (WebFetch
it). **Never write a URL from memory, never guess one, never build one by
editing another.** If a search doesn't confirm the fact cleanly, drop that
question and ask something else.

### 2. One source per question — the important one
Each question must cite a source URL that **no other question in the round
uses.** Compare on **hostname + path**, ignoring query strings and anchors.

The failure mode this prevents: you find one rich article (say, about the
Michelin Guide) and mine three questions out of it. The round then repeats
itself and the family notices immediately. **If one search hands you three good
facts about the same subject, use exactly one and go and search for something
else.**

### 3. Category quotas
Six categories, **minimum `perCategory` (default 5) questions each**:

- History
- Food & drink
- Geography
- Culture & the arts
- Sport & games
- Language & everyday life

After drafting, **count per category**. Any category short of quota gets a
**top-up pass** — search again for that category specifically. Then
**interleave** the final order so the round never runs in blocks of five from
the same category.

### 4. Question quality
- **Short, unambiguous answers**: one name, date, place, number, or phrase.
- **Timeless**: nothing that turns on this season's results, a current
  officeholder, or a record that may since have been broken.
- **No trick wording**: no double negatives, no "which of these is NOT".
- **Balance the Channel**: vary which side each question belongs to — aim for a
  rough balance between France, Britain, and questions that genuinely span both
  (`side`: `"france"` / `"britain"` / `"both"`).
- **A note per question**: one sentence of colour for the host to read out
  after the reveal.

### 5. Don't repeat past nights
Read **every** existing `rounds/round-*.json` first and avoid those questions
and close variations of them.

## Procedure

1. **Read the past.** Read `rounds/index.json` and every `rounds/round-*.json`.
   Note the next round number `N` and build a mental list of what's been asked.
2. **Research per category.** For each of the six categories, search and verify
   facts until you have at least `perCategory` solid questions. Open each source
   (WebFetch) and record the exact final URL. Keep a running set of used
   `hostname + path` and skip any fact whose source collides. This is a good
   place to fan out: one research pass per category, overshooting slightly so
   you can drop weak ones. When delegating research, instruct helpers to return
   only URLs they actually opened.
3. **Draft.** Write each question with `category`, `side`, `question`,
   `answer`, `accept` (alternative acceptable answers), `note`, and `source`.
4. **Count & top up.** Tally per category. Top up any that are short.
5. **Interleave.** Order so no two adjacent questions share a category where
   avoidable, and the sides vary.
6. **Assemble** `rounds/round-N.json` (schema below) and set `written` to
   today's date (`YYYY-MM-DD`).
7. **Check.** Run `python3 scripts/check.py`. It fails if any question lacks a
   source or if two questions share a source (host+path). Fix and re-run until
   it passes.
8. **Index.** Regenerate `rounds/index.json` — an array of
   `{ id, number, title, written, count }`, **newest first**.
9. **Ship.** `git add`, commit with a clear message, and
   `git push -u origin claude/noexquizzes-build-riy90x` (retry with backoff on
   network errors). GitHub Pages picks it up.
10. **Report.** Give the per-category counts and the live URL
    (https://mrgrob.github.io/NoExQuizzes/). If a category couldn't be filled
    with solid, verified questions, **say so** rather than padding it.

## round-N.json schema

```json
{
  "id": "round-3",
  "number": 3,
  "title": "Round 3 — a short evocative subtitle",
  "written": "2026-07-29",
  "questions": [
    {
      "category": "History",
      "side": "both",
      "question": "In what year was the Entente Cordiale signed?",
      "answer": "1904",
      "accept": ["1904"],
      "note": "It ended centuries of on-off conflict and still frames the relationship today.",
      "source": "https://www.britannica.com/event/Entente-Cordiale"
    }
  ]
}
```

- `id` is `"round-" + number`.
- `side` is one of `"france"`, `"britain"`, `"both"`.
- `accept` is a list (may be empty) of extra answers the host should accept.
- `source` must be a real URL you opened, unique within the round on host+path.

## If in doubt

If searching a category turns up nothing solid, come back and tell the user
rather than padding it with something half-remembered. Interrupting is better
than shipping something plausible and wrong.
