---
name: create-france-quizz
description: >-
  Produce one evening's round for the NoExQuizzes family quiz where EVERY
  question is about France, and — whenever a genuine link exists — reaches
  across to Britain/the UK. Load this whenever the user asks for a
  France-focused or "on the go" round — e.g. "quiz about France", "a French
  round", "fais un quiz sur la France", "France quiz for tonight", "on the go
  France quiz", or the /create-france-quizz command. Same procedure, format,
  and quality rules as create-quizz-session; only the subject focus differs.
  Writes rounds/round-N.json, refreshes rounds/index.json, runs the check,
  commits, pushes, and reports per-category counts and the live URL.
---

# Create a France-focused quiz round

This is the sibling of `create-quizz-session`. **Everything about how you work
is identical** — the no-API-key rule, verify-before-write, one unique source per
question, the six category quotas, timeless answers, no trick wording, a note
per question, no repeats, the round JSON format, `scripts/check.py`, and
ship + report. Read that skill for the full procedure; only re-read the
differences below.

You are still the generator. **No API key, no backend, no build step.** You
research and verify here in the session and commit finished JSON that the static
player reads.

## What is different: the France lens

1. **Every question is about France.** French history, French places, French
   food and drink, French art and culture, French sport, the French language
   and everyday life in France. If a question isn't really *about France*, it
   doesn't belong in this round.

2. **Reach for the UK whenever it's genuine.** This family is British and lives
   in France, so the best questions are the ones that touch both shores. When a
   fact has a real, non-forced British or UK connection, prefer that framing:
   - the Hundred Years' War, the Norman Conquest, Waterloo, the Entente
     Cordiale, D-Day and Normandy;
   - French words that live in English (and English words the French borrowed);
     Roland Garros vs. Wimbledon, the Six Nations, the Channel Tunnel;
     French chefs who made their name in London, Impressionists who painted the
     Thames, the Auld Alliance, and so on.
   - Mark these `"side": "both"`.
   Never bolt on a fake link. If the honest answer is that a fact is purely
   French, keep it and mark `"side": "france"`.

3. **Sides.** Expect this round to be mostly `"france"` and `"both"`, with **no
   pure `"britain"` questions** — a question with no French content doesn't fit
   here. Aim for a healthy share of `"both"` (roughly a third when the material
   allows) so the cross-Channel thread is felt, without straining for it.

4. **Categories stay the same six**, each still filled through the French lens:
   - History → French/Franco-British history
   - Food & drink → French cheeses, wines, dishes, cooking terms
   - Geography → French rivers, mountains, régions, cities, coasts, islands
   - Culture & the arts → French writers, painters, composers, cinema, chanson
   - Sport & games → Tour de France, Roland Garros, French football/rugby,
     pétanque (bring in the UK where it's real: Six Nations, cross-Channel ties)
   - Language & everyday life → French words in English, franglais, French
     customs and institutions, la bise, everyday life in France

## Parameters (all optional)

Same as `create-quizz-session`: `theme` (a French sub-theme, e.g. "Paris",
"the south", "the belle époque"), `difficulty` (`gentle` / `pub` / `fiendish`,
default `pub`), `perCategory` (default 5 → 30). "On the go" simply means: same
quality, produced on demand — if the user wants a quicker round, they can ask
for a smaller `perCategory` (e.g. 3 → 18), but never drop a category below the
requested count by padding; if a category can't be filled with solid,
verified, genuinely-French questions, say so.

## Procedure (delta from create-quizz-session)

Follow the full procedure in `create-quizz-session`, with these changes:

- **Read the past first** — every `rounds/round-*.json`, from *both* skills, so
  a France round never repeats a question already asked (or a close variant).
- When researching each category, keep the French lens: verify each fact by
  searching, take the source URL from the result you actually opened, and keep
  every source unique within the round (host + path).
- Give the round a title that signals its French focus (e.g.
  `"Round N — Un soir en France"` or similar).
- Count per category, top up any shortfall with another France-specific search,
  interleave so categories don't run in blocks, and vary `france` / `both` so
  the round doesn't sit on one framing for long.
- Assemble `rounds/round-N.json`, run `python3 scripts/check.py` until it
  passes, refresh `rounds/index.json` (newest first), commit, push to
  `claude/noexquizzes-build-riy90x`, and report per-category counts, the
  france/both split, and the live URL (https://mrgrob.github.io/NoExQuizzes/).

## Same format as every round

The JSON schema, the `side` values (`"france"` / `"britain"` / `"both"` — you
just won't use `"britain"` here), and the `accept` / `note` / `source` fields
are exactly as documented in `create-quizz-session`. That's what lets the same
`index.html` play these rounds with no changes.
