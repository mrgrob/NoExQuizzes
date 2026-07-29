# NoExQuizzes

A Franco-British family quiz. The family is British and lives in France; every
question is in English. One person hosts and reads the questions aloud from a
phone or tablet in the living room, everyone else answers on paper.

**Live site:** https://mrgrob.github.io/NoExQuizzes/

## The one architectural rule: no API key, anywhere

There is **no API key** in this project. Not in the frontend, not in GitHub
Secrets, not in a serverless function. There is no backend and no build step.

The published site (`index.html`) is a single self-contained static file. It
does exactly one clever thing: it fetches JSON from the `rounds/` folder and
plays it. That's the whole runtime.

The questions themselves are written by **Claude, in a working session**, and
committed as finished JSON. Claude is the generator — it researches and
verifies each question, then commits it. GitHub Pages serves the result. No
key is ever needed because nothing is ever generated at runtime.

If you (or a tool) ever reach for an Anthropic API call, a `.env`, a backend,
or a build step — stop. That is the design being violated, not a missing
piece.

## How to ask for a new round

In a Claude Code session on this repo, just ask — in English or French:

> "fais la session de ce soir" · "new quiz round" · "quiz for tonight"

or run `/create-quizz-session`.

Claude loads the skill at
[`.claude/skills/create-quizz-session/SKILL.md`](.claude/skills/create-quizz-session/SKILL.md)
and follows it: it reads past rounds to avoid repeats, researches and
**verifies each fact by opening its source**, enforces **one unique source per
question** and the **per-category quotas**, writes `rounds/round-N.json`,
refreshes `rounds/index.json`, commits, pushes, and reports the per-category
counts and the live URL.

You can give it options: a **theme**, a **difficulty**
(`gentle` / `pub` / `fiendish`), or **questions per category**. It uses sensible
defaults (pub difficulty, 5 per category → 30 questions) when you don't.

### A France-focused round

For a round where **every question is about France** — reaching across to the UK
whenever there's a genuine link — ask for that instead:

> "a quiz about France" · "fais un quiz sur la France" · "France quiz for tonight"

or run `/create-france-quizz`. It loads
[`.claude/skills/create-france-quizz/SKILL.md`](.claude/skills/create-france-quizz/SKILL.md),
which follows the exact same procedure, format, and quality rules as above — only
the subject focus changes (sides skew `france` / `both`, never a pure `britain`
question). Both skills write into the same `rounds/` folder and play in the same
page, and each reads the other's past rounds so they never repeat a question.

## Repository layout

```
index.html            The player. Self-contained; no build, no dependencies.
rounds/
  index.json          [{ id, number, title, written, count }], newest first.
  round-1.json        One evening's questions.
  round-2.json        ...
scripts/
  check.py            Verifies every question has a source and no two in a
                      round share one (host + path). Run: python3 scripts/check.py
.claude/skills/
  create-quizz-session/SKILL.md   The procedure Claude follows to build a round.
  create-france-quizz/SKILL.md    Same procedure, France-focused (with UK links).
README.md
```

## The design

France and Britain fly the same three colours, so the interface uses only that
shared set: a deep navy background, warm paper-white type, **blue** for a French
question, **red** for a British one, **white** for one that spans both. The
signature element is the *Channel strip* along the top of the card — a marker
slides from "France" to "Britain" to show which country the current question is
about before the host even speaks.

## Marking

Each round self-marks. The host reveals the answer, taps **Right** or
**Missed it**, and the page keeps a running team score. At the end it shows the
score out of N and a printable answer sheet listing every question, answer and
source.
