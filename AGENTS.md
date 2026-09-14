# DIA GALLERY — MANDATORY AI / DEVELOPER INSTRUCTIONS

You are working on the independent Dia Gallery project.

Repository:

`samanehtavazoe-afk/dia-gallery`

Production branch:

`dia`

Production server path:

`/opt/dia-gallery`

Production domain:

`https://samaneh.filmjadiid.ir`

Before making ANY meaningful change:

1. Read `PROJECT_HISTORY.md`.
2. Read `CHANGELOG.md`.
3. Read `DIA_START_HERE.md`.
4. Inspect the actual current code related to the task.
5. Confirm the current branch and SHA.
6. Do not guess missing business rules.

The actual current code is the primary source of truth.

Never assume context from another ChatGPT account.

Never import another business's products, data, rules, credentials or workflows.

Do not modify `main`.

Work only on branch `dia` unless the owner explicitly decides otherwise.

Do not:

- force push
- delete production Docker volumes
- overwrite `.env`
- use `git reset --hard`
- use `git clean -fd`
- drop the production database
- introduce destructive migrations casually
- enable Digikala API automatically
- enable Telegram integration automatically

The existing local Digikala commission calculation is intentional.

The absence of Digikala Open API integration is intentional.

The delta-based inventory synchronization using
`inventory_applied_quantity` is critical and must not be replaced by
full-quantity deduction on every edit.

Historical SaleLine values such as cost and Digikala fee are snapshots.

Do not silently recalculate history when current product cost/settings change.

For significant changes:

- inspect relevant code first
- implement narrowly
- add/update tests
- run Django check
- check migrations
- review diff
- commit
- push
- update `CHANGELOG.md`
- update `PROJECT_HISTORY.md` when architecture/rules change
- give exact deployment command

Never say production changed merely because GitHub changed.

Production success requires actual deployment/server evidence.
