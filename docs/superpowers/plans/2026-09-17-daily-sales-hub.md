# Daily Sales Hub Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing daily-sales page into a four-card daily hub with correct cash-vs-platform settlement behavior, a dedicated Holder direct-sale workflow, and holiday-aware Jalali calendar presentation.

**Architecture:** Reuse `SaleOrder`, `SaleLine`, `ProductVariant`, stock delta services, and existing finance accounts. Add small focused service helpers for payment classification and platform receivable reporting; keep the generic invoice editor as the underlying entry screen, but route into it from the daily hub with constrained channel/payment choices. Add a dedicated Holder order model/service because Holder deposits and money-received-by-Mehr cannot be represented safely by the generic platform flow.

**Tech Stack:** Django, PostgreSQL, Django templates, `jdatetime`, existing Docker Compose test environment.

**Spec:** `docs/superpowers/specs/2026-09-17-daily-sales-hub-design.md`

## Global Constraints
- Production branch is `dia`; implementation occurs on `finance-panel` until verification.
- Preserve existing delta-based `inventory_applied_quantity` behavior.
- Do not add Digikala API integration.
- Do not overwrite production `.env` or delete Docker volumes.
- No destructive git/database commands.
- Cash enters bank only when actually received; platform sales remain receivables until settlement.

---

### Task 1: Payment classification for sale orders

**Files:**
- Modify: `dia_core/services.py`
- Modify: `dia_core/views.py`
- Test: `dia_core/tests.py`

**Interfaces:**
- Produces: `sale_payment_mode(*, sales_channel, payment_provider) -> str`, returning `cash` or `platform_receivable`.
- Produces: `default_sale_payment_status(*, sales_channel, payment_provider) -> str`, returning a `SaleOrder.PaymentStatus` value.

- [ ] **Step 1: Write failing service tests**

Add tests asserting:
```python
self.assertEqual(sale_payment_mode(sales_channel=digikala, payment_provider=None), "platform_receivable")
self.assertEqual(sale_payment_mode(sales_channel=basalam, payment_provider=None), "platform_receivable")
self.assertEqual(sale_payment_mode(sales_channel=site, payment_provider=None), "cash")
self.assertEqual(sale_payment_mode(sales_channel=site, payment_provider=snapp), "platform_receivable")
self.assertEqual(sale_payment_mode(sales_channel=site, payment_provider=digipay), "platform_receivable")
self.assertEqual(sale_payment_mode(sales_channel=site, payment_provider=torobpay), "platform_receivable")
```
Also assert the corresponding default status is `PENDING` for platform receivables and `RECEIVED` for cash.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.SalePaymentClassificationTests -v 2
```
Expected: failure because the helper does not exist yet.

- [ ] **Step 3: Implement minimal helpers**

In `services.py`, classify channel codes `digikala` and `basalam` as platform receivables regardless of provider; classify provider codes `snapp`, `digipay`, and `torobpay` as platform receivables; otherwise classify as cash.

- [ ] **Step 4: Use the helper in `sale_day`**

Replace the current `selected_provider ? PENDING : RECEIVED` default with `default_sale_payment_status(...)`. Preserve explicit existing order status while editing.

- [ ] **Step 5: Run focused tests and existing sale tests**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.SalePaymentClassificationTests dia_core.tests.FinanceSaleOrderTests -v 2
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add dia_core/services.py dia_core/views.py dia_core/tests.py
git commit -m "fix: classify platform sales as pending receivables"
```

---

### Task 2: Daily four-card sales hub

**Files:**
- Modify: `dia_core/views.py`
- Modify: `dia_core/urls.py`
- Modify: `templates/dia_core/sale_day.html`
- Test: `dia_core/tests.py`

**Interfaces:**
- Daily hub accepts a selected `mode` query value: `digikala`, `site`, `basalam`, `holder`.
- Existing generic sale editor remains available only for the selected non-Holder mode.

- [ ] **Step 1: Write failing template/view tests**

Test GET of a sale day without `mode` and assert the page contains all four labels:
```text
دیجی‌کالا
سایت
باسلام
فروش قالب
```
Assert the generic invoice form marker `کالاهای فاکتور` is absent before a card is selected.

- [ ] **Step 2: Verify RED**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.DailySalesHubTests -v 2
```
Expected: FAIL because current page renders the invoice editor immediately.

- [ ] **Step 3: Add hub mode handling**

In `sale_day`, read `mode` from GET/POST and validate against `digikala/site/basalam/holder`. When no mode is chosen, render only date summary and four cards. Keep order totals visible only when meaningful for the selected mode.

- [ ] **Step 4: Constrain each generic mode**

For `digikala`, force/select Digikala channel and hide payment provider choice.
For `basalam`, force/select Basalam channel and hide payment provider choice.
For `site`, force/select Site channel and show only cash/direct plus SnappPay/DigiPay/TorobPay providers.
For `holder`, do not render the generic SaleOrder editor; render the Holder form from Task 4.

- [ ] **Step 5: Verify GREEN**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.DailySalesHubTests dia_core.tests.FinanceSaleOrderTests -v 2
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add dia_core/views.py dia_core/urls.py templates/dia_core/sale_day.html dia_core/tests.py
git commit -m "feat: add daily sales card hub"
```

---

### Task 3: Platform receivable summary

**Files:**
- Modify: `dia_core/services.py`
- Modify: `dia_core/views.py`
- Modify: `templates/dia_core/finance.html`
- Test: `dia_core/tests.py`

**Interfaces:**
- Produces: `platform_receivable_totals() -> dict[str, int]` keyed by `digikala`, `basalam`, `snapp`, `digipay`, `torobpay`.
- A sale contributes only while its order status is `PENDING`.

- [ ] **Step 1: Write failing tests**

Create pending and received orders for each channel/provider. Assert pending Digikala/Basalam/provider sales appear in the correct bucket and received orders do not.

- [ ] **Step 2: Verify RED**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.PlatformReceivableTests -v 2
```
Expected: FAIL because the summary helper does not exist.

- [ ] **Step 3: Implement receivable totals**

For each pending order, calculate gross line sales plus customer-collected shipping/provider surcharge, then subtract snapshotted channel/provider fees, taxes, shipping cost, and Digikala fee to obtain the amount expected from the platform. Do not change bank cash.

- [ ] **Step 4: Show finance cards**

Render one compact `طلب از پلتفرم‌ها` section in `finance.html` with separate rows for Digikala, Basalam, SnappPay, DigiPay, and TorobPay.

- [ ] **Step 5: Verify GREEN**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.PlatformReceivableTests dia_core.tests.FinanceDashboardTests -v 2
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add dia_core/services.py dia_core/views.py templates/dia_core/finance.html dia_core/tests.py
git commit -m "feat: report platform receivables"
```

---

### Task 4: Holder direct-sale workflow

**Files:**
- Modify: `dia_core/models.py`
- Create: `dia_core/migrations/0006_holderdirectorder_holderdirectreceipt.py`
- Modify: `dia_core/services.py`
- Modify: `dia_core/views.py`
- Modify: `templates/dia_core/sale_day.html`
- Test: `dia_core/tests.py`

**Interfaces:**
- New `HolderDirectOrder` stores date, customer, quantities for small/medium/large, unit prices, order total, note.
- New `HolderDirectReceipt` stores order, amount, receipt_type (`deposit/full/balance`), recipient (`samaneh/mehr`), date, note.
- Produces: `record_holder_receipt(order, amount, receipt_type, recipient, date, note="")`.

- [ ] **Step 1: Write failing model/service tests**

Assert a Holder order can store three size quantities and compute remaining customer balance as `order_total - sum(receipts)`.
Assert a Samaneh receipt increases bank cash exactly once.
Assert a Mehr receipt does not change bank cash and is queryable as money held by Mehr.

- [ ] **Step 2: Verify RED**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.HolderDirectSaleTests -v 2
```
Expected: FAIL because models/services do not exist.

- [ ] **Step 3: Add models and migration**

Create the two models with positive-amount constraints and recipient/type choices. Generate migration and inspect it before applying.

- [ ] **Step 4: Implement receipt accounting**

When recipient is `samaneh`, add the receipt to the cash account through an `AccountEntry` with an idempotent reference tied to the receipt id. When recipient is `mehr`, create no bank entry and do not create a Mehr receivable automatically.

- [ ] **Step 5: Connect Holder quantities to inventory**

Map small/medium/large Holder variants explicitly by the existing Holder catalog and apply inventory deltas through the existing stock movement pattern. Editing an order must apply only the quantity delta.

- [ ] **Step 6: Add Holder form to the Holder card**

Render customer, three quantities, prices, order total, amount received, receipt type, recipient, remaining balance, and note. Show prior Holder orders/receipts for the selected date below the form.

- [ ] **Step 7: Run model/view/inventory tests**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.HolderDirectSaleTests dia_core.tests.DiaStockSyncTests -v 2
```
Expected: PASS.

- [ ] **Step 8: Commit**

```bash
git add dia_core/models.py dia_core/migrations/0006_holderdirectorder_holderdirectreceipt.py dia_core/services.py dia_core/views.py templates/dia_core/sale_day.html dia_core/tests.py
git commit -m "feat: add holder direct sales and receipts"
```

---

### Task 5: Jalali calendar holiday presentation

**Files:**
- Modify: `dia_core/dateutils.py`
- Modify: `dia_core/views.py`
- Modify: `templates/dia_core/sales_calendar.html`
- Test: `dia_core/tests.py`

**Interfaces:**
- `month_calendar` continues to return the existing calendar structure.
- Each day metadata entry gains `is_friday`, `is_holiday`, and `holiday_title`.

- [ ] **Step 1: Write failing Friday/holiday metadata tests**

Assert Friday detection is correct for known dates and that configured holiday dates render with `is_holiday=True` and a title.

- [ ] **Step 2: Verify RED**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.SalesCalendarHolidayTests -v 2
```
Expected: FAIL because holiday metadata is absent.

- [ ] **Step 3: Implement holiday metadata without changing date storage**

Keep Gregorian persistence and Jalali conversion. Add a small holiday data provider for the required 1405 calendar dates and expose Friday/holiday state to the template.

- [ ] **Step 4: Update calendar template**

Give Fridays and official holidays distinct styling and show the holiday title in small text while preserving the `فروش ثبت شده` marker.

- [ ] **Step 5: Verify GREEN**

Run:
```bash
docker compose exec web python manage.py test dia_core.tests.SalesCalendarHolidayTests dia_core.tests.DiaIsolationTests -v 2
```
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add dia_core/dateutils.py dia_core/views.py templates/dia_core/sales_calendar.html dia_core/tests.py
git commit -m "feat: mark holidays in sales calendar"
```

---

### Task 6: Full verification and deployment preparation

**Files:**
- No new feature files unless verification finds a defect.

**Interfaces:**
- All earlier task interfaces remain unchanged.

- [ ] **Step 1: Run migration drift check**

```bash
docker compose exec web python manage.py makemigrations --check --dry-run
```
Expected: `No changes detected`.

- [ ] **Step 2: Run Django check**

```bash
docker compose exec web python manage.py check
```
Expected: no issues.

- [ ] **Step 3: Run full test suite**

```bash
docker compose exec web python manage.py test dia_core -v 2
```
Expected: all tests PASS.

- [ ] **Step 4: Run git whitespace check and status**

```bash
git diff --check
git status -sb
```
Expected: no whitespace errors; branch contains only intended committed changes.

- [ ] **Step 5: Push feature branch**

```bash
git push origin finance-panel
```

- [ ] **Step 6: Only after successful verification, fast-forward `dia` and deploy using the existing safe deployment procedure**

Do not claim production is updated until `sudo bash deploy.sh` reports `SUCCESS: DIA GALLERY BASE DEPLOYED` and the deployed SHA matches the merged `dia` commit.