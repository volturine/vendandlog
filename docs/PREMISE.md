# Vendandlog — Premise

A bazaar where everything is public by design. People post listings, talk, and meet — and the whole history stays visible forever.

## The core idea

Most marketplaces optimize for the transaction and hide everything else. Vendandlog inverts this: **transparency is the product**. When every listing, every negotiation, and every outcome is permanently visible, trust stops being a promise and becomes a verifiable public record.

## Pillars

### 1. Listings never disappear

Under normal circumstances, a listing — once created — never disappears. Sold, expired, or withdrawn listings remain part of the public record. This permanence is what makes every other feature meaningful: reputation, price history, and negotiation patterns all depend on history that cannot be quietly deleted.

### 2. Conversations become public

- Every listing has conversations between the seller and interested buyers.
- **Once a listing is sold, all conversations related to it become visible to everyone.**
- Either the seller or the buyer can **prematurely unhide** a conversation tied to a listing — you never have to wait for the sale to expose how someone behaves.

### 3. Trust is a public score

- Buyers rate sellers; sellers rate buyers. Two-sided by default.
- There must be an additional way to **highlight scammers on both sides** — beyond a numeric rating.
- Each user has a **trust score**, conceptually similar to HackerNews karma: earned slowly through real, visible behavior, and visible to all.
- Because listings and conversations never vanish, a trust score is always backed by inspectable evidence.

### 4. No transactions (yet)

Vendandlog is **not** a payment platform. It is a place to post things, find things, talk, negotiate, and agree where to meet. Money changes hands offline, between people. This keeps the platform's incentives clean: we are not paid by the transaction, so we have no reason to hide anything.

## Deliberate features

- **Wishlist with AI matching** — describe what you're looking for; AI matches your wishlist against new listings as they appear.
- **AI-assisted negotiation** — AI can handle communication and negotiation on your behalf, up to the point of "shaking hands". The actual meeting and exchange stay human.
- **Open API** — extensions and integrations are first-class. The API is a product feature, not an internal detail.
- **Dynamically evolving categories** — categories form trees that can grow and reshape as the bazaar's inventory evolves, instead of a fixed, hardcoded taxonomy.

## Design constraints

- **Very modular architecture** — frontend, backend, and independent services, loosely coupled. But modularity must never dilute the soul of the app (see the invariants in `AGENTS.md`).
- **Simplistic but adaptive UI** — the interface stays minimal and calm, yet adapts to any kind of listing. Adaptability comes from the data model, not from bespoke per-category UI.
- **The soul cannot be lost** — transparency, permanence, public trust, and no money on-platform are not features to be traded away; they are the reason the app exists.

## What this is not

- Not a payment processor, escrow service, or auction house.
- Not a feed optimized for engagement — it's a record optimized for trust.
- Not a place where history can be rewritten.
