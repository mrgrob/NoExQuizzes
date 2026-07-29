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

### Topics that play well (a growing pool)

Beyond the obvious, these have landed well and are fair game (each still routed
through one of the six categories):

- **England vs France football** — the two national teams, their meetings,
  players, stadiums and history (Sport & games).
- **Film**, including big franchises the family enjoys such as the **Jurassic
  Park / Jurassic World** films, plus Franco-British cinema (Culture & the
  arts). Non-Franco-British film facts take `side: "neutral"`.
- **French ↔ English loanwords, both directions** — French words in English and
  English/franglais words in French (Language & everyday life).
- **Provence** — its geography, food and drink, and history (Geography, Food &
  drink, History).
- **Cultural differences between Britain and France** — everyday customs and
  institutions, kept to factual, single-answer points (Language & everyday
  life).
- **UK pop & rock** — British pop and rock music. This is a recognised **extra
  category** (`"UK pop & rock"`), not one of the core six. On a music-leaning
  night, use it as one of the round's category slots (e.g. in place of Sport &
  games), still five questions with all the usual rules. The player gives it
  its own colour and `scripts/check.py` accepts it.
- **Inventions** — French and British inventions and discoveries, old or recent,
  including things built jointly (Concorde, the Channel Tunnel). Another
  recognised **extra category** (`"Inventions"`) with its own colour; use it as
  a category slot when the night calls for it. Lean into "both" for joint
  Franco-British engineering.

**Include a photo or two.** Most rounds play better with a couple of `image`
questions mixed in (a landmark → "which région?", a painting → "who painted
it / which museum?"). The image is the star; make sure the answer isn't given
away by the picture or its (reveal-only) caption.

**Always include sport and movies.** Every round must carry **at least one or
two Sport & games questions** and **at least one or two film/movie questions**
(the movies live in Culture & the arts). Even on a themed night that swaps a
category out, keep a sport question and a film question somewhere in the round —
the family always wants them.

**Difficulty per theme.** Tailor to what the family knows. They are devoted
Jurassic Park fans and have lived in Provence for 40 years — so pitch **Jurassic
Park and Provence questions at expert level** (deep, specific facts, not tourist
trivia), and lean on `options` to keep the fiendish ones fair.

Add to this list as new themes prove themselves. A themed night can lean the
whole round toward a few of these while still filling all six categories.

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
- `side` is one of `"france"`, `"britain"`, `"both"`, or `"neutral"`. Use
  `"neutral"` only for a question that is genuinely neither French nor British
  (e.g. a Jurassic Park film fact) — the player shows it with a centred, grey
  marker. Prefer a real Franco-British angle whenever one honestly exists.
- `accept` is a list (may be empty) of extra answers the host should accept.
- `source` must be a real URL you opened, unique within the round on host+path.
- `options` is **optional**: for a **difficult** question you may add an array of
  **exactly 4** short answer choices, including the correct `answer` verbatim
  (or one of its `accept` forms). The player then shows the four choices and
  highlights the right one at the reveal. Leave it out for open-answer
  questions. Use it for the harder facts, not the easy ones — a round of all
  multiple-choice is too easy; a few well-placed ones make the fiendish
  questions fair.

Example with options:

```json
{
  "category": "Geography", "side": "france",
  "question": "The Gorges du Verdon reaches a maximum depth of roughly how many metres?",
  "answer": "700 metres", "accept": ["700", "700 m"],
  "options": ["300 metres", "500 metres", "700 metres", "1,000 metres"],
  "note": "The Verdon has cut a limestone ravine up to about 700 m deep.",
  "source": "https://en.wikipedia.org/wiki/Verdon_Gorge"
}
```

### Optional media: images and a music blind test

Questions may carry media, all **key-free** (loaded in the viewer's browser; the
site hosts nothing except any local audio you commit). Add sparingly — roughly
**one image question and one blind-test question per round**.

- `image` — an image URL. The player shows it large; write the question so the
  answer is what the picture asks (e.g. a photo of a landmark → *"Which région
  of France is this?"*, answer a région). **Use freely-licensed images only**
  (Wikimedia Commons: public domain / CC-BY-SA). Prefer a stable Commons URL of
  the form `https://commons.wikimedia.org/wiki/Special:FilePath/<File name>.jpg`.
  Add `imageCredit` (e.g. `"Photo: <author>, CC BY-SA 4.0, Wikimedia Commons"`)
  and set `source` to the Commons file page. Optionally `imageAlt`.
- `youtube` — a YouTube video id (just the id, e.g. `"fJ9rUzIMcZQ"`). The player
  shows a "▶ Play the clip" button that loads YouTube's own licensed player, so
  a **famous-song blind test is legal without hosting anything or any key**.
  Write the question as *"Name this song / artist"*; put the reveal in `answer`.
- `audio` — a URL to an audio file for a self-contained clip. **Only host
  public-domain or Creative-Commons audio** (e.g. Musopen) under `rounds/audio/`;
  never commit copyrighted pop/rock — use `youtube` for that.

Every media question still needs a real `source` and obeys the one-unique-source
rule. Note: this build environment cannot fetch external media, so when adding
image/youtube URLs, flag that the human should confirm they load.

## If in doubt

If searching a category turns up nothing solid, come back and tell the user
rather than padding it with something half-remembered. Interrupting is better
than shipping something plausible and wrong.
