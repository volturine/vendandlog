# Vendandlog

A transparent bazaar: listings, conversations, and trust — all public by design. No payments, just people agreeing to meet.

**Status:** skeleton implementation. Read [`docs/PREMISE.md`](docs/PREMISE.md) before writing any code.

## The soul (never lose this)

These are product invariants. Any architecture, feature, or refactor that violates them is wrong, no matter how elegant:

1. **Radical transparency** — listings never disappear under normal circumstances. Sold listings stay. Their history stays.
2. **Conversations become public** — once a listing is sold, all conversations tied to it are visible to everyone. Either party may also unhide a conversation prematurely.
3. **Trust is earned, public, and two-sided** — buyers rate sellers, sellers rate buyers, scammers on both sides get flagged. A HackerNews-karma-like trust score is a first-class citizen.
4. **No transactions** — the platform never touches money. People post, find, talk, and meet. Keep it that way until an explicit decision says otherwise.
5. **Modularity must serve the soul** — the architecture is very modular, but modularity is a means, never a reason to dilute the invariants above.

## Stack

- **Frontend:** SvelteKit 5 (runes) + Tailwind CSS 4, adapter-static SPA build. Bun for packages.
- **Backend:** FastAPI + SQLModel + SQLite (via uv). Serves the built frontend in production — one process, one port.
- Design language: scrapscache tokens (Keep pastels, hairline cards, class-based dark mode) + Atelier editorial accents (Fraunces serif hero, provenance stamps). Reference mockups: [`docs/mockups/`](docs/mockups/) (`index.html` is the hub).

## Layout

```
packages/frontend    # SvelteKit 5 SPA — browse, listing detail, profile, new listing
packages/backend     # FastAPI — listings + immutable event log, conversations, ratings, flags
packages/services/   # independent services (one subfolder each) — future: AI matching, trust scoring
docs/                # premise, PRDs, architecture, mockups
```

## Commands

```bash
just install    # backend uv sync + frontend bun install
just dev        # API :8000 + Vite dev server :3000 (live preview, /api proxied)
just prod       # build frontend, FastAPI serves it + API from :8000
just check      # ruff + svelte-check
just test       # backend pytest (the soul invariants live in tests/test_api.py)
just format     # ruff + prettier
```

- Frontend: `bun add` / `bun remove` — never hand-edit `package.json`.
- Python: `uv add` / `uv remove` in `packages/backend` — never hand-edit the lockfile by hand.
- Backend package deps: Python >= 3.12, no Postgres needed for the skeleton (SQLite file `vendandlog.db`, delete it to reseed).

## Auth (skeleton)

The client declares who acts via the `X-Acting-As: <handle>` header; the UI has an identity picker in the header. Real auth is future work — the API shape will not change.

## Definition of done

`just check` && `just test` before done or review. Add backend tests for new/changed backend behavior — especially anything touching the invariants above.

## Principles

- Choose the simplest implementation that fully meets current requirements. No speculative abstractions.
- Grow in layers: smallest end-to-end working version first, then capabilities on top of a working product.
- Keep modules loosely coupled with clear ownership; services communicate over explicit contracts (the open API is a product feature, not an afterthought).
- Categories evolve dynamically as trees — do not hardcode a fixed taxonomy (the current `category` string field is the seed of that; the UI must not become per-category bespoke).
- UI stays simplistic; adaptability to any listing comes from the data model, not from per-category bespoke UI.
- Prefer established, well-maintained libraries over reimplementation.
