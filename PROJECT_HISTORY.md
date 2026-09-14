# DIA GALLERY — PROJECT HISTORY & AI HANDOFF

Documentation snapshot: 2026-09-14 19:14:23 UTC

Baseline commit before this documentation commit:

`4f5b2e188c201bc91d64e20b2f759ec57ae88d4f`

Repository:

`samanehtavazoe-afk/dia-gallery`

Production branch:

`dia`

Git remote on production server:

`git@github-dia:samanehtavazoe-afk/dia-gallery.git`

Production domain:

`https://samaneh.filmjadiid.ir`

Production server path:

`/opt/dia-gallery`

Application version:

`dia-base-v1`

---

# 1. WHY THIS FILE EXISTS

This document is the main context/handoff document for Dia Gallery.

It is intentionally detailed enough that a new developer or a new ChatGPT account with zero previous conversation history can understand:

- what this project is
- why it was created
- what currently works
- how data is modeled
- how inventory is changed
- how Digikala commission is calculated
- how reports and finance work
- how deployment works
- which integrations are intentionally absent
- which files are important
- what must not be changed accidentally
- how future changes should be tested and deployed

A future AI MUST NOT depend on memory from another ChatGPT account.

Read the repository itself.

The priority of truth is:

1. current source code on branch `dia`
2. current Git state and migrations
3. this `PROJECT_HISTORY.md`
4. `CHANGELOG.md`
5. `DIA_START_HERE.md`
6. assumptions

If documentation and code disagree, inspect the code and fix the documentation.

Never silently guess.

---

# 2. PRODUCT IDENTITY

Product name:

**Dia Gallery**

This is an independent internal business-management dashboard for Dia Gallery.

It is not a public storefront.

Its purpose is to give Dia Gallery a simple operational panel for:

- daily sales
- Digikala commission calculations
- profit reporting
- finished-goods inventory
- purchases
- returns
- stock adjustments
- financial accounts
- payments and receipts
- product/variant definitions
- basic management reporting

The UI language is primarily Persian.

The application uses an RTL responsive dark interface.

---

# 3. IMPORTANT HISTORY / ORIGIN

The current Dia Gallery application was initially designed by examining another business-management panel as a visual and functional reference.

That reference project is NOT a dependency of this repository.

The Dia project was deliberately separated so that another business's:

- products
- inventory
- bank accounts
- customers
- suppliers
- Telegram configuration
- API credentials
- production workflows
- raw-material workflows
- business-specific rules
- database
- secrets
- Git history

would not become Dia Gallery data or runtime behavior.

A clean Django app named:

`dia_core`

was created for Dia Gallery.

Only the active Dia code was copied into this repository.

The old reference application's business app was NOT copied as an active dependency.

The `dia` branch of this repository was created as an **orphan branch** so its Git history is independent.

The repository originally contained an unrelated Next.js starter on `main`.

That `main` branch was intentionally preserved.

Original main baseline at migration time:

`14dd1d5570aa86cecf236cf21e994f3cb5b7a31c`

Rollback branch created before Dia bootstrap:

`before-dia-bootstrap-14dd1d55`

The Dia branch was bootstrapped from a verified Dia source baseline whose final reference SHA was:

`8a8ee1ed49f22d80011a05f72427aced05fc84e7`

That SHA is historical provenance only.

The production application must use THIS repository and THIS `dia` branch.

Do not deploy the old reference repository.

Do not merge `main` into `dia`.

---

# 4. REPOSITORY / PRODUCTION RULES

Production repository:

`samanehtavazoe-afk/dia-gallery`

Production branch:

`dia`

Production path:

`/opt/dia-gallery`

Production domain:

`samaneh.filmjadiid.ir`

Docker Compose project:

`dia-gallery`

Django settings module:

`config.settings`

Main Django business app:

`dia_core`

Production must remain isolated from every other app/server project.

Do not reuse another project's:

- PostgreSQL volume
- database
- `.env`
- SECRET_KEY
- API credentials
- Telegram token
- backups
- Docker volume names
- application directory

---

# 5. HIGH-LEVEL STACK

Backend:

- Python
- Django
- PostgreSQL 16
- Gunicorn

Frontend:

- Django templates
- Persian RTL UI
- Tabler CSS via CDN
- Vazirmatn font via CDN
- Chart.js on dashboard where required
- responsive desktop/mobile layout

Infrastructure:

- Docker
- Docker Compose
- Caddy
- automatic HTTPS

Timezone:

`Asia/Tehran`

Django language:

`fa-ir`

---

# 6. IMPORTANT FILES

## `dia_core/models.py`

Database/domain models.

## `dia_core/views.py`

Main business/UI behavior.

## `dia_core/services.py`

Critical reusable business logic, especially:

- Digikala fee calculation
- inventory synchronization
- returns
- adjustments
- account balances

## `dia_core/dateutils.py`

Jalali date parsing, formatting and calendar logic.

## `dia_core/urls.py`

Active application routes.

## `dia_core/tests.py`

Business regression tests.

## `dia_core/management/commands/seed_base.py`

Creates only generic initial application rows.

It must never seed real business catalog/data.

## `dia_core/management/commands/ensure_admin.py`

Creates/ensures the configured admin user.

## `config/settings.py`

Django/project/database/security configuration.

## `config/urls.py`

Login/logout/admin and Dia app routing.

## `templates/dia_core/`

All active Dia Gallery application templates.

## `templates/registration/login.html`

Login screen.

## `compose.yml`

Production PostgreSQL/web/Caddy stack.

## `Dockerfile`

Application image.

## `entrypoint.sh`

Container startup sequence.

## `deploy.sh`

Production deployment/update script.

## `Caddyfile`

Production reverse proxy and TLS domain.

## `.env`

Production secrets/config.

NEVER commit `.env`.

## `.github/workflows/dia-check.yml`

CI safety/test workflow.

## `PROJECT_HISTORY.md`

This document.

## `CHANGELOG.md`

Future significant changes.

## `AGENTS.md`

Mandatory instructions for AI/developers.

---

# 7. ACTIVE URLS

Application routes:

`/`

Dashboard.

`/sales/`

Jalali daily-sales calendar.

`/sales/select/<jy>/<jm>/<jd>/`

Select/create a SaleDay from a Jalali date.

`/sales/<day_id>/`

Manual daily sales entry.

`/report/`

Sales/profit report.

`/inventory/`

Current finished-goods inventory and stock adjustment.

`/returns/`

Return entry/history.

`/purchase/`

Purchase-of-the-day entry.

`/finance/`

Accounts, payments and receipts.

`/settings/`

Products, variants, sizes, colors and application settings.

Django authentication routes also exist for login/logout.

Django admin is enabled.

There are deliberately NO Digikala Open API routes.

---

# 8. AUTHENTICATION

Normal application views use Django authentication and require login.

Deployment environment uses:

`APP_ADMIN_USERNAME`

and:

`APP_ADMIN_PASSWORD`

Default admin username convention:

`diaadmin`

`ensure_admin` does NOT contain a default production password.

If `APP_ADMIN_PASSWORD` is absent, automatic admin password creation/update is skipped.

Never commit production passwords.

Never print an existing production password into Git history.

---

# 9. DATA MODEL

## Size

Fields:

- `name`
- `sort_order`
- `active`

Used to define product sizes.

No sizes are seeded automatically.

---

## Color

Fields:

- `name`
- `code`
- `active`

No colors are seeded automatically.

---

## Product

Fields:

- `code`
- `title`
- `active`
- `note`

`code` is unique.

No product catalog is seeded automatically.

---

## ProductVariant

A sellable inventory unit.

Combination of:

- Product
- Size
- Color

Also stores:

- `default_sale_price`
- `unit_cost`
- `active`

Unique constraint:

Product + Size + Color

A variant's `unit_cost` represents the CURRENT cost used for future sales.

Historical sales store a snapshot separately.

---

## StockLocation

Generic inventory location.

Fresh setup creates only:

key:

`main`

title:

`موجودی اصلی`

The current application assumes this is the primary finished-goods stock.

---

## StockBalance

Current stock quantity for:

Variant + StockLocation

The combination is unique.

`qty` is an integer and CAN become negative.

Do not add an artificial non-negative constraint without an explicit business decision.

---

## InventoryMovement

Immutable-style inventory movement history.

Movement types:

- purchase
- sale
- return
- adjust

Fields include:

- date
- movement_type
- variant
- location
- delta
- reference
- note
- created_at

This ledger is important for debugging stock changes.

Do not update StockBalance directly from random views.

Use the service functions whenever possible.

---

## SaleDay

One logical daily-sales container per Gregorian database date.

`date` is unique.

The UI presents dates in Jalali format.

---

## SaleLine

A product variant's sale row for one SaleDay.

Important fields:

- day
- variant
- quantity
- inventory_applied_quantity
- sale_price
- unit_cost_snapshot
- digikala_fee_unit

Unique:

SaleDay + Variant

`unit_cost_snapshot` preserves historical cost.

`digikala_fee_unit` preserves the calculated commission snapshot for that sale price.

`inventory_applied_quantity` is critical for safe inventory synchronization.

Do not remove it casually.

---

## PurchaseLine

A product-variant purchase for a date.

Fields:

- date
- variant
- quantity
- inventory_applied_quantity
- unit_cost
- note

Unique:

Date + Variant

Inventory is synchronized using the difference between desired quantity and previously applied quantity.

---

## ReturnRecord

Records customer/product returns.

A return increases stock.

Quantity must be greater than zero.

---

## InventoryAdjustment

Explicit manual stock correction.

`delta` may be positive or negative.

A zero adjustment is invalid.

Every adjustment should also create an InventoryMovement.

---

## Account

Generic financial account.

Fields:

- title
- opening_balance
- active

No bank/account names are seeded.

Dia Gallery defines its own accounts.

---

## AccountEntry

Generic balance-changing ledger row.

Fields include:

- account
- date
- delta
- title
- reference
- note

Current balance is:

opening balance + sum(AccountEntry.delta)

---

## Payment

Represents money paid FROM an account.

A payment must create a negative AccountEntry.

---

## Receipt

Represents money received INTO an account.

A receipt must create a positive AccountEntry.

---

## AppSetting

Generic key/value application settings.

Currently used for:

- Digikala commission percentage
- Digikala processing percentage
- Digikala processing minimum
- VAT percentage
- taxable part at processing floor
- low-stock threshold

---

# 10. DAILY SALES LOGIC

Daily sales are entered manually.

This project deliberately does NOT retrieve Digikala orders through an API.

For each active variant the daily-sales page allows:

- quantity
- sale price

When a SaleLine is first created:

- its current variant cost is copied into `unit_cost_snapshot`
- its current Digikala fee is calculated and copied into `digikala_fee_unit`

This preserves historical reporting.

If the variant cost changes tomorrow, yesterday's COGS should not silently change.

If a sale price changes, the Digikala fee snapshot is recalculated.

The application calculates:

gross sales

minus:

Digikala fee

minus:

COGS

equals:

profit

Margin is:

profit / gross sales * 100

when gross sales is non-zero.

---

# 11. CRITICAL INVENTORY SYNC RULE

Sales and purchases use a DELTA synchronization design.

This is one of the most important implementation details in the project.

For sales:

target quantity = SaleLine.quantity

already applied quantity = SaleLine.inventory_applied_quantity

difference:

`delta = target - applied`

Stock change:

`StockBalance.qty -= delta`

Then:

`inventory_applied_quantity = target`

Example:

Starting stock:

10

Sale initially saved:

3

Stock becomes:

7

Sale edited from 3 to 5:

Only 2 more units are removed.

Stock becomes:

5

Sale edited from 5 to 1:

4 units are restored.

Stock becomes:

9

This prevents double inventory deductions when editing an existing sale.

Purchases use the same concept in the opposite direction:

`StockBalance.qty += delta`

Never replace this logic with "subtract entire quantity on every save".

That would corrupt inventory.

---

# 12. NEGATIVE INVENTORY

Current stock is allowed to become negative.

This is intentional in the base system.

A future developer must not silently clamp stock to zero.

If Dia Gallery later wants strict stock blocking, implement it only after explicit approval because it changes operational behavior.

---

# 13. PURCHASE LOGIC

`/purchase/` is the purchase-of-the-day workflow.

A purchase:

- increases finished-goods stock
- creates/updates a PurchaseLine
- creates inventory movement(s)
- uses delta synchronization
- can update the ProductVariant's current `unit_cost`

The current `ProductVariant.unit_cost` is for FUTURE transactions.

Already-created SaleLines retain their historical `unit_cost_snapshot`.

This separation is important for accurate historical profit.

---

# 14. RETURN LOGIC

A return:

- creates a ReturnRecord
- increases StockBalance
- creates an InventoryMovement with type `return`

A return quantity must be positive.

---

# 15. INVENTORY ADJUSTMENT LOGIC

Manual correction is available from inventory.

Adjustment:

- requires non-zero delta
- may be positive or negative
- modifies StockBalance
- creates InventoryAdjustment
- creates InventoryMovement with type `adjust`

Use adjustment for explicit corrections instead of silently changing database stock values.

---

# 16. DIGIKALA BEHAVIOR

Dia Gallery sells through Digikala.

Therefore the system intentionally keeps:

- daily Digikala sales
- Digikala commission calculation
- Digikala commission reporting

BUT:

There is currently NO Digikala Open API integration.

There is:

- no network Digikala API client
- no Digikala API token
- no automatic order downloader
- no automatic product deactivation
- no Telegram approval bot
- no Digikala Excel/API importer

Do not add these merely because Digikala is mentioned.

Only add external integration if the owner explicitly requests it.

---

# 17. DIGIKALA COMMISSION FORMULA

The formula is local and configurable through AppSetting.

Default generic settings:

`digikala_commission_percent = 24`

`digikala_processing_percent = 7`

`digikala_processing_floor = 36000`

`digikala_vat_percent = 10`

`digikala_floor_taxable_part = 18000`

Calculation for one sold unit:

Let:

`price = sale price`

Commission:

`commission = price * commission_percent`

Raw processing:

`raw_processing = price * processing_percent`

If raw processing is below the processing floor:

`processing = processing_floor`

and:

`taxable_processing = floor_taxable_part`

Otherwise:

`processing = raw_processing`

and:

`taxable_processing = processing / 2`

VAT:

`vat = (commission + taxable_processing) * vat_percent`

Final fee:

`commission + processing + vat`

The final value is rounded to the nearest integer using ROUND_HALF_UP.

Reference regression case with default settings:

sale price:

`100000`

fee:

`64200`

This result is covered by automated tests.

If Digikala changes its official fees later, update settings/formula deliberately and add/adjust tests.

Do not hardcode a new number in templates.

---

# 18. REPORTING

The report page supports:

- current Jalali month
- today
- all data
- custom Jalali start/end date range

It calculates:

- gross sales
- Digikala fees
- COGS
- profit
- quantity
- margin

It also groups results by product code.

Detailed report rows are based on SaleLine snapshot values.

Historical cost/fee reporting should remain stable.

---

# 19. DASHBOARD

Dashboard currently shows:

- today's sales/profit
- current Jalali month's sales/profit
- recent sales/profit chart
- low-stock alerts
- quick navigation

The chart currently uses up to the latest 14 sale days with actual sale quantities.

Low-stock threshold is configurable with:

`low_stock_threshold`

Default:

`10`

Alerts currently inspect main stock and active variants/products.

---

# 20. JALALI DATES

The UI is Persian/Jalali oriented.

The database uses normal Django `DateField` values.

`dia_core/dateutils.py` converts between Jalali and Gregorian.

Important calendar code handles Esfand safely by testing whether day 30 is valid.

Regression tests cover Esfand behavior for multiple years.

Do not replace the Jalali helper casually.

When adding new date-entry pages, reuse existing date parsing/formatting helpers.

---

# 21. UI / DESIGN

Current UI goals:

- Persian RTL
- dark navy visual system
- orange accent
- mobile responsive
- simple operational dashboard
- desktop sidebar
- mobile bottom navigation
- minimal dependency complexity

Main application template:

`templates/dia_core/base.html`

The current branding is:

`Dia Gallery`

Do not reintroduce branding from any reference project.

---

# 22. FRESH DATABASE / SEED POLICY

A fresh Dia Gallery database must NOT automatically contain:

- products
- sizes
- colors
- variants
- sales
- inventory balances
- financial accounts
- people
- bank names
- customer names
- supplier names
- another business's data

`seed_base` intentionally creates only:

main StockLocation

plus generic application settings.

This isolation is tested by CI.

---

# 23. CURRENT DEFAULT SETTINGS CREATED BY seed_base

Stock location:

key:

`main`

title:

`موجودی اصلی`

Settings:

- Digikala commission percentage
- processing percentage
- processing floor
- VAT percentage
- floor taxable portion
- low-stock threshold

`get_or_create` is used so seed_base is safe to run repeatedly.

Do not turn seed_base into a business-data importer.

---

# 24. FINANCE LOGIC

Finance is deliberately generic.

There are no predefined bank names.

Users define accounts themselves.

Account balance:

`opening_balance + SUM(AccountEntry.delta)`

Payments reduce an account.

Receipts increase an account.

When expanding finance functionality, preserve a ledger-oriented design.

Avoid storing a second independent "balance" field that can drift from entries unless there is a strong transactional reason.

---

# 25. DEPLOYMENT ARCHITECTURE

Production uses Docker Compose.

Services:

## db

PostgreSQL 16 Alpine.

Uses dedicated Dia database volume.

## web

Django/Gunicorn application.

## caddy

TLS/reverse proxy.

Ports:

80

443 TCP

443 UDP

The deployment uses separate named volumes:

- `dia_gallery_pgdata`
- `dia_gallery_caddy_data`
- `dia_gallery_caddy_config`

Do not rename/remove production volumes casually.

Doing so can appear to "delete" the database by attaching a fresh volume.

---

# 26. CONTAINER STARTUP

`entrypoint.sh` runs:

Django migrations

then:

collectstatic

then:

`seed_base`

then:

`ensure_admin`

then starts Gunicorn.

Gunicorn currently runs with:

2 workers

2 threads per worker

timeout 60 seconds

This is appropriate for the current lightweight base deployment.

---

# 27. DEPLOYMENT PROCESS

Production code path:

`/opt/dia-gallery`

Normal deployment/update:

`sudo bash deploy.sh`

The deploy script should:

- require branch `dia`
- refuse a dirty Git tree
- fetch branch `dia`
- use fast-forward-only update
- preserve an existing `.env`
- create `.env` only on first install
- validate Docker Compose
- build/start services
- run Django system check
- print basic data isolation counts
- print final commit SHA

The success marker is:

`SUCCESS: DIA GALLERY BASE DEPLOYED`

A GitHub commit DOES NOT mean production is deployed.

Production is only considered updated after deployment output is checked.

---

# 28. PRODUCTION ENVIRONMENT

`.env` contains secrets and production-specific configuration.

Expected categories:

- DEBUG
- SECRET_KEY
- ALLOWED_HOSTS
- CSRF_TRUSTED_ORIGINS
- DB_NAME
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT
- APP_ADMIN_USERNAME
- APP_ADMIN_PASSWORD

Never commit `.env`.

Never replace production `.env` with `.env.example`.

Never rotate production database credentials accidentally during normal deploy.

---

# 29. CADDY

Production domain:

`samaneh.filmjadiid.ir`

Caddy reverse-proxies traffic to:

`web:8000`

Caddy handles HTTPS automatically.

If the application is down but Caddy is running, inspect web/container logs before changing DNS.

---

# 30. SECURITY BASELINE

Current Django settings include:

- CSRF protection
- secure session cookies in production
- secure CSRF cookies in production
- trusted proxy SSL header
- X-Frame-Options DENY
- content-type sniff protection
- Django password validators
- login-required application pages

Production uses a random Django SECRET_KEY generated during initial deploy.

Secrets stay outside Git.

---

# 31. EXTERNAL-INTEGRATION SAFETY

The CI contains a guard against accidental external integrations in the active runtime.

Patterns such as:

- requests.
- httpx.
- open-api/v1
- Digikala token variables
- Telegram bot token

are intentionally guarded in active Dia code.

If a future feature genuinely requires an external API, update this protection consciously and document the decision in CHANGELOG.

Never disable the guard simply to make CI green without understanding why it triggered.

---

# 32. LEGACY BUSINESS SAFETY

The active Dia source is checked so business-specific identifiers from the historical reference project do not leak back into runtime code.

Do not copy old modules wholesale from another repository.

If a useful feature exists elsewhere:

understand the behavior

then implement it using Dia's own models/rules.

Do not import unknown data/business assumptions.

---

# 33. CI

Workflow:

`.github/workflows/dia-check.yml`

Expected checks include:

- install dependencies
- Django system check
- migration drift check
- migrations against PostgreSQL 16
- seed isolation check
- unit tests
- legacy-business identifier guard
- external API guard

When changing models:

create a real migration.

Then verify:

`python manage.py makemigrations dia_core --check --dry-run`

shows no missing migration after the migration has been created.

Never deploy unreviewed model changes without migrations.

---

# 34. EXISTING REGRESSION TEST INTENT

Important behavior already tested includes:

- fresh seed does not create business catalog/data
- absent Digikala API routes remain absent
- default local Digikala commission calculation
- safe sales inventory delta synchronization
- Jalali/Esfand calendar behavior

Future features should add tests rather than weakening these existing tests.

---

# 35. CHANGE SAFETY PROCEDURE

Before any significant code change:

Confirm repository:

`samanehtavazoe-afk/dia-gallery`

Confirm branch:

`dia`

Inspect:

`git status`

Inspect current commit:

`git rev-parse HEAD`

Read:

`PROJECT_HISTORY.md`

Read:

`CHANGELOG.md`

Inspect the actual files affected by the requested change.

Do not guess architecture from filenames alone.

For significant or risky changes, create a rollback branch/tag before deployment.

Never use destructive commands casually, including:

`git reset --hard`

`git clean -fd`

database volume deletion

database drop

destructive migration

force push

unless the owner explicitly understands and authorizes the destructive operation.

Prefer reversible migrations and incremental commits.

---

# 36. AFTER EVERY SIGNIFICANT CHANGE

The developer/AI should:

- implement the requested change
- run relevant tests
- run Django system check
- verify migration state if models changed
- inspect `git diff`
- commit to branch `dia`
- push
- append a concise entry to `CHANGELOG.md`
- update `PROJECT_HISTORY.md` if architecture/business invariants changed
- give exact deployment commands
- wait for actual server output before claiming production success

A Git commit alone is not evidence that production is running the new code.

---

# 37. WHAT FUTURE AI MUST NOT DO

Do not assume knowledge from another ChatGPT account.

Do not invent Dia business rules.

Do not invent products/prices/accounts.

Do not use another business's catalog.

Do not add Digikala API integration unless explicitly requested.

Do not add Telegram integration unless explicitly requested.

Do not seed real operational data.

Do not merge `main` into `dia`.

Do not overwrite production `.env`.

Do not delete Docker volumes.

Do not force-push production branch.

Do not claim deployment succeeded without server evidence.

Do not change commission logic silently.

Do not change inventory semantics silently.

---

# 38. KNOWN INTENTIONAL SIMPLICITY

This is a BASE application.

It was intentionally left generic so Dia Gallery can now define its own exact workflows.

Some likely future needs may include:

- improved account/financial reporting
- custom Dia-specific product workflows
- additional dashboards
- expense management
- more detailed purchase management
- export to Excel
- user roles/permissions
- backup tooling
- richer reports
- public/storefront integrations
- notification systems

These are NOT automatically requirements.

The owner should decide them.

Implement only requested features.

---

# 39. CURRENT BUSINESS BOUNDARIES

The current system manages finished products.

There is no active:

- raw-material inventory
- textile/fabric workflow
- production/tailor workflow
- supplier debt workflow
- automatic Digikala synchronization
- Telegram notification bot
- multi-brand legacy logic

If Dia Gallery later needs these, design them for Dia from scratch rather than reviving unrelated historical modules.

---

# 40. DEBUGGING CHECKLIST

If the website fails after deployment, inspect in this order:

Current Git branch/SHA.

Docker services:

`docker compose -p dia-gallery ps`

Web logs:

`docker compose -p dia-gallery logs --tail=200 web`

Database logs if needed:

`docker compose -p dia-gallery logs --tail=200 db`

Caddy logs if HTTP/TLS issue:

`docker compose -p dia-gallery logs --tail=200 caddy`

Django system check:

`docker compose -p dia-gallery exec -T web python manage.py check`

Migrations:

`docker compose -p dia-gallery exec -T web python manage.py showmigrations`

Do not immediately delete/recreate containers or volumes when diagnosing.

---

# 41. DATABASE BACKUP PRINCIPLE

Before risky database/model operations, take a PostgreSQL backup.

Production database persistence is more important than convenience.

Never treat a container rebuild as a database backup.

Docker named volume persistence and database backup are separate concepts.

A future production-hardening task should add a formal automated backup/restore procedure.

---

# 42. SOURCE-OF-TRUTH RULE FOR AI

A new ChatGPT should begin every meaningful engineering task by reading the current repository rather than relying only on this document.

This document describes the baseline architecture.

Git is live and may change later.

If `CHANGELOG.md` contains newer decisions, those newer decisions override older descriptions here.

If actual source and docs differ:

do not guess.

Inspect commit history and current implementation.

Then update stale documentation.

---

# 43. OWNER INTENT

The project was intentionally handed to Dia Gallery so that the owner can now ask a separate ChatGPT account to change the project independently.

The new ChatGPT is expected to act like the project's continuing technical maintainer.

It should be able to:

- inspect GitHub
- understand current architecture
- safely modify branch `dia`
- preserve data
- run tests
- commit changes
- provide exact deployment commands
- document new decisions

It must not need access to the conversations that originally created the base application.

That is the reason this document exists.

---

# 44. REQUIRED READ ORDER FOR A NEW AI

Before first modification, read in this order:

`PROJECT_HISTORY.md`

`DIA_START_HERE.md`

`AGENTS.md`

`CHANGELOG.md`

`dia_core/models.py`

`dia_core/services.py`

`dia_core/views.py`

`dia_core/urls.py`

`dia_core/dateutils.py`

`dia_core/tests.py`

`config/settings.py`

`config/urls.py`

`compose.yml`

`entrypoint.sh`

`deploy.sh`

`.github/workflows/dia-check.yml`

Then inspect whatever templates/files are relevant to the requested feature.

Do not make the first change before understanding those files.

---

# 45. BASELINE SUMMARY

At handoff, Dia Gallery has an independent Django/PostgreSQL management panel running at:

`https://samaneh.filmjadiid.ir`

Its active production branch is:

`dia`

Its central application is:

`dia_core`

It manages:

sales

Digikala commission

profit

finished-goods inventory

purchases

returns

stock adjustments

accounts

payments

receipts

catalog definitions

It intentionally contains no other business's operational data and no external Digikala/Telegram API integration.

This baseline should remain safe, understandable and reversible as new Dia-specific features are added.
