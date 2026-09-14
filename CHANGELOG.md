# Dia Gallery Changelog

This file records significant product, architecture, data-model and deployment changes.

Newest entries should be added at the top.

Do not use this file for every tiny cosmetic edit; record changes that a future maintainer needs to understand.

---

## 2026-09-14 — Complete AI handoff documentation

Baseline before documentation:

`4f5b2e188c201bc91d64e20b2f759ec57ae88d4f`

Added:

- comprehensive `PROJECT_HISTORY.md`
- stronger `AGENTS.md`
- persistent change-documentation protocol

Purpose:

A completely separate ChatGPT account or developer can now understand and maintain the project without access to the conversations that originally created it.

No runtime/business logic changed.

---

## 2026-09-14 — Dia Gallery production base deployed

Dia Gallery base application successfully brought online at:

`https://samaneh.filmjadiid.ir`

Production branch:

`dia`

Production server path:

`/opt/dia-gallery`

Architecture:

- Django
- PostgreSQL 16
- Docker Compose
- Gunicorn
- Caddy HTTPS
- dedicated `dia_core` application

Core features at initial handoff:

- dashboard
- Jalali sales calendar
- manual daily sales
- local Digikala commission calculation
- gross/fee/COGS/profit reporting
- finished-product inventory
- delta-safe inventory synchronization
- daily purchases
- returns
- stock adjustments
- generic finance/accounts
- products/sizes/colors/variants
- responsive Persian dark UI

External Digikala API integration intentionally absent.

Telegram integration intentionally absent.

Fresh database contains no real business catalog/accounts/sales/inventory.

---

## 2026-09-14 — Independent repository migration

Production application moved into independent repository:

`samanehtavazoe-afk/dia-gallery`

The `dia` branch was created as an orphan branch.

The unrelated pre-existing Next.js `main` branch was preserved.

Original main baseline:

`14dd1d5570aa86cecf236cf21e994f3cb5b7a31c`

Rollback branch:

`before-dia-bootstrap-14dd1d55`

Verified Dia reference source baseline used for the clean extraction:

`8a8ee1ed49f22d80011a05f72427aced05fc84e7`

Only active Dia application code was migrated.

Legacy reference business runtime/history was deliberately excluded.
