# DIA GALLERY — START HERE

This is the independent Dia Gallery management system.

## Production

- Domain: samaneh.filmjadiid.ir
- Server path: /opt/dia-gallery
- Production branch: dia
- Django app: dia_core
- Docker Compose project: dia-gallery

## Important

This repository is independent.

Do not import business data or business-specific rules from another project.

The active application is:

- dia_core/
- config/
- templates/dia_core/
- templates/registration/

## Current features

- dark responsive dashboard
- Jalali daily sales calendar
- manual daily Digikala sales
- local Digikala commission calculation
- sales / commission / COGS / profit reports
- finished-goods inventory
- inventory movement ledger
- purchase of the day
- returns
- stock adjustments
- financial accounts
- payments and receipts
- product / size / color / variant definitions

## Digikala

Digikala sales and commission calculations are intentional.

There is NO Digikala Open API integration.

There is NO Digikala API token.

There is NO Telegram integration.

## Fresh data rule

A new installation must NOT seed:

- products
- sizes
- colors
- sales
- inventory balances
- accounts
- personal/business data

Only generic application settings may be initialized.

## AI / developer instruction

Read this file before changing the project.

Do not infer Dia Gallery business rules from another repository.
