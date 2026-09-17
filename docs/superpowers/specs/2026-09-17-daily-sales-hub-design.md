# Daily Sales Hub Design

## Goal
Replace the current crowded daily-sales invoice screen with a simple daily hub inspired by the approved Darma workflow, while preserving existing inventory delta logic and financial history.

## Daily calendar
- Keep the existing Jalali monthly calendar and Gregorian-backed dates.
- Mark Fridays distinctly.
- Add official-holiday metadata so holidays can be visually marked without changing stored sale dates.
- Selecting a day opens the daily sales hub.

## Daily sales hub
The selected date is shown prominently. The page shows four independent cards instead of immediately rendering the full invoice editor:
1. Digikala
2. Website
3. Basalam
4. Holder direct sales

Each card opens or filters to its own manual-entry workflow. Existing SaleOrder/SaleLine rows remain the underlying accounting/inventory records.

## Payment semantics
### Digikala
- No payment-method choice in the Digikala flow.
- New Digikala sales default to pending settlement.
- Sale registration reduces inventory but does not increase bank cash.
- Net amount due after channel fees belongs to platform receivables until settlement.

### Website
Website sales may use exactly these payment methods:
- Cash/direct payment: received immediately and treated as cash/bank.
- SnappPay: pending platform receivable.
- DigiPay: pending platform receivable.
- TorobPay: pending platform receivable.

### Basalam
- Basalam sales default to pending settlement.
- They remain platform receivables until settlement.

## Holder direct sale
Holder uses a dedicated workflow rather than the generic invoice screen. It records:
- customer/reference
- small quantity
- medium quantity
- large quantity
- unit prices / order total
- amount currently received
- receipt type: deposit, full settlement, remaining-balance payment
- money recipient: Samaneh or Mehr
- remaining customer balance
- note

If Samaneh receives the money, the received amount is cash/bank. If Mehr receives it, the amount is recorded as customer money held by Mehr and does not enter Samaneh's bank. It must not automatically become Samaneh's receivable from Mehr; only the actual amount later determined to be due from Mehr becomes a Mehr receivable.

## Inventory rules
- Existing ProductVariant and delta-based `inventory_applied_quantity` behavior must remain unchanged.
- Generic product sales reduce the exact sold variant (product/size/color).
- Holder direct sales reduce the exact size quantities.
- Editing a sale changes stock only by the delta, as today.

## Finance behavior
- Cash/direct receipts affect the cash account only when money is actually received.
- Digikala/Basalam/SnappPay/DigiPay/TorobPay stay outside bank cash until settlement.
- Platform settlement later converts platform receivable into bank cash without duplicating revenue.
- Existing counterparty and supplier balances remain independent from platform receivables.

## UI constraints
- Preserve the current Dia Gallery visual system; copy Darma's information architecture, not its branding.
- The daily page should show cards first and detailed forms only after the user chooses a card.
- Avoid one long page containing every invoice and every product at once.

## Safety / compatibility
- Production branch remains `dia`; feature work stays on `finance-panel` until verified.
- Preserve production `.env` and database volumes.
- No Digikala external API integration is added.
- No destructive git/database commands.
- Existing historical snapshots, commissions, and inventory movements must continue to work.