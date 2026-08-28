# Vendandlog

A transparent bazaar: listings, conversations, and trust — all public by design. No payments, just people agreeing to meet.

**Status:** pre-implementation. Stack not yet chosen. Read [`docs/PREMISE.md`](docs/PREMISE.md) before writing any code.

## The soul (never lose this)

These are product invariants. Any architecture, feature, or refactor that violates them is wrong, no matter how elegant:

1. **Radical transparency** — listings never disappear under normal circumstances. Sold listings stay. Their history stays.
2. **Conversations become public** — once a listing is sold, all conversations tied to it are visible to everyone. Either party may also unhide a conversation prematurely.
3. **Trust is earned, public, and two-sided** — buyers rate sellers, sellers rate buyers, scammers on both sides get flagged. A HackerNews-karma-like trust score is a first-class citizen.
4. **No transactions** — the platform never touches money. People post, find, talk, and meet. Keep it that way until an explicit decision says otherwise.
5. **Modularity must serve the soul** — the architecture is very modular, but modularity is a means, never a reason to dilute the invariants above.

## Layout

Monorepo, modeled after data-forge:

```
packages/frontend    # UI — simplistic, but adaptive to any listing type
packages/backend     # core API, listings, conversations, trust
packages/services/   # independent services (one subfolder each) — e.g. AI matching, AI negotiation, trust scoring
docs/                # premise, PRDs, architecture
```

## Principles

- Choose the simplest implementation that fully meets current requirements. No speculative abstractions.
- Grow in layers: smallest end-to-end working version first, then capabilities on top of a working product.
- Keep modules loosely coupled with clear ownership; services communicate over explicit contracts (the open API is a product feature, not an afterthought).
- Categories evolve dynamically as trees — do not hardcode a fixed taxonomy.
- UI stays simplistic; adaptability to any listing comes from the data model, not from per-category bespoke UI.
- Prefer established, well-maintained libraries over reimplementation.
