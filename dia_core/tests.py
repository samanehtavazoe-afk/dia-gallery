from datetime import date

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.urls import Resolver404, resolve

from .dateutils import month_calendar
from .models import Account, Color, Product, ProductVariant, SaleDay, SaleLine, Size, StockBalance
from .services import digikala_fee_for_unit, main_location, sync_sale_inventory


class DiaIsolationTests(TestCase):
    def setUp(self):
        call_command("seed_base", verbosity=0)

    def test_legacy_core_is_not_installed(self):
        self.assertNotIn("core", settings.INSTALLED_APPS)
        self.assertTrue(any("dia_core" in item for item in settings.INSTALLED_APPS))

    def test_fresh_seed_has_no_business_data(self):
        self.assertEqual(Product.objects.count(), 0)
        self.assertEqual(SaleDay.objects.count(), 0)
        self.assertEqual(StockBalance.objects.count(), 0)
        self.assertEqual(Account.objects.count(), 0)

    def test_digikala_api_routes_do_not_exist(self):
        with self.assertRaises(Resolver404):
            resolve("/digikala/")
        with self.assertRaises(Resolver404):
            resolve("/digikala/orders/")

    def test_reference_commission_formula_is_kept_local(self):
        self.assertEqual(digikala_fee_for_unit(100_000), 64_200)

    def test_jalali_calendar_handles_esfand(self):
        for year in (1404, 1405, 1406):
            cal = month_calendar(year, 12)
            days = [day for week in cal["weeks"] for day in week if day]
            self.assertEqual(days[0], 1)
            self.assertIn(days[-1], (29, 30))
            self.assertEqual(len(days), days[-1])


class DiaStockSyncTests(TestCase):
    def setUp(self):
        call_command("seed_base", verbosity=0)
        size = Size.objects.create(name="TEST", sort_order=1)
        color = Color.objects.create(name="TEST COLOR", code="T")
        product = Product.objects.create(code="TEST-P")
        self.variant = ProductVariant.objects.create(
            product=product,
            size=size,
            color=color,
            default_sale_price=100_000,
            unit_cost=20_000,
        )
        self.balance = StockBalance.objects.create(variant=self.variant, location=main_location(), qty=10)
        self.day = SaleDay.objects.create(date=date(2026, 9, 14))

    def test_sale_edit_roundtrip_changes_only_delta(self):
        line = SaleLine.objects.create(
            day=self.day,
            variant=self.variant,
            quantity=3,
            sale_price=100_000,
            unit_cost_snapshot=20_000,
            digikala_fee_unit=digikala_fee_for_unit(100_000),
        )
        sync_sale_inventory(line)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.qty, 7)

        line.quantity = 5
        line.save(update_fields=["quantity"])
        sync_sale_inventory(line)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.qty, 5)

        line.quantity = 1
        line.save(update_fields=["quantity"])
        sync_sale_inventory(line)
        self.balance.refresh_from_db()
        self.assertEqual(self.balance.qty, 9)

from django.test import TestCase
from django.utils import timezone

from dia_core.models import (
    Business,
    Color,
    Product,
    ProductVariant,
    SaleDay,
    SaleLine,
    SaleOrder,
    SalesChannel,
    Size,
    StockLocation,
    VariantChannelPrice,
)
from dia_core.services import (
    sale_metrics,
    stock_for,
    sync_sale_inventory,
)


class FinanceSaleOrderTests(TestCase):
    def setUp(self):
        self.location = StockLocation.objects.create(
            key="main",
            title="Main",
            active=True,
        )

        self.business = Business.objects.create(
            code="test-business",
            title="Test Business",
            active=True,
        )
        self.channel = SalesChannel.objects.create(
            code="site",
            title="Site",
            active=True,
        )
        self.size = Size.objects.create(
            name="L",
            sort_order=1,
        )
        self.color = Color.objects.create(
            name="Black",
        )

        self.product1 = Product.objects.create(
            code="P1",
            title="Product 1",
            business=self.business,
        )
        self.product2 = Product.objects.create(
            code="P2",
            title="Product 2",
            business=self.business,
        )

        self.variant1 = ProductVariant.objects.create(
            product=self.product1,
            size=self.size,
            color=self.color,
            default_sale_price=100000,
            unit_cost=40000,
        )
        self.variant2 = ProductVariant.objects.create(
            product=self.product2,
            size=self.size,
            color=self.color,
            default_sale_price=200000,
            unit_cost=80000,
        )

        VariantChannelPrice.objects.create(
            variant=self.variant1,
            sales_channel=self.channel,
            sale_price=125000,
        )

        self.day = SaleDay.objects.create(
            date=timezone.localdate(),
        )

        self.order = SaleOrder.objects.create(
            day=self.day,
            business=self.business,
            sales_channel=self.channel,
            payment_status=SaleOrder.PaymentStatus.RECEIVED,
            shipping_collected=160000,
            shipping_cost=120000,
        )

    def test_channel_price_exists_and_default_fallback_is_possible(self):
        channel_price = VariantChannelPrice.objects.get(
            variant=self.variant1,
            sales_channel=self.channel,
        )

        self.assertEqual(channel_price.sale_price, 125000)
        self.assertEqual(self.variant2.default_sale_price, 200000)

    def test_multi_line_order_updates_inventory_by_delta(self):
        stock1 = stock_for(self.variant1)
        stock2 = stock_for(self.variant2)

        stock1.qty = 10
        stock1.save(update_fields=["qty"])

        stock2.qty = 20
        stock2.save(update_fields=["qty"])

        line1 = SaleLine.objects.create(
            day=self.day,
            order=self.order,
            variant=self.variant1,
            business=self.business,
            sales_channel=self.channel,
            quantity=2,
            sale_price=125000,
            unit_cost_snapshot=40000,
        )
        line2 = SaleLine.objects.create(
            day=self.day,
            order=self.order,
            variant=self.variant2,
            business=self.business,
            sales_channel=self.channel,
            quantity=3,
            sale_price=200000,
            unit_cost_snapshot=80000,
        )

        sync_sale_inventory(line1)
        sync_sale_inventory(line2)

        stock1.refresh_from_db()
        stock2.refresh_from_db()

        self.assertEqual(stock1.qty, 8)
        self.assertEqual(stock2.qty, 17)

        line1.quantity = 5
        line1.save(update_fields=["quantity"])
        sync_sale_inventory(line1)

        stock1.refresh_from_db()
        line1.refresh_from_db()

        self.assertEqual(stock1.qty, 5)
        self.assertEqual(line1.inventory_applied_quantity, 5)

    def test_shipping_is_order_level_not_line_level(self):
        line1 = SaleLine.objects.create(
            day=self.day,
            order=self.order,
            variant=self.variant1,
            business=self.business,
            sales_channel=self.channel,
            quantity=1,
            sale_price=125000,
            unit_cost_snapshot=40000,
        )
        line2 = SaleLine.objects.create(
            day=self.day,
            order=self.order,
            variant=self.variant2,
            business=self.business,
            sales_channel=self.channel,
            quantity=1,
            sale_price=200000,
            unit_cost_snapshot=80000,
        )

        metrics1 = sale_metrics(line1)
        metrics2 = sale_metrics(line2)

        gross = metrics1["gross"] + metrics2["gross"]
        cogs = metrics1["cogs"] + metrics2["cogs"]

        profit = (
            gross
            + self.order.shipping_collected
            - self.order.shipping_cost
            - cogs
        )

        self.assertEqual(gross, 325000)
        self.assertEqual(cogs, 120000)
        self.assertEqual(profit, 245000)

        self.assertFalse(hasattr(line1, "shipping_cost_snapshot"))
        self.assertFalse(hasattr(line2, "shipping_cost_snapshot"))

class FinanceSettingsSetupTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        self.user = get_user_model().objects.create_user(
            username="finance-settings-test",
            password="test-pass-123",
        )
        self.client.force_login(self.user)

        self.product = Product.objects.create(
            code="SETTINGS-P1",
            title="Settings Product",
        )

    def test_settings_page_has_clean_title_and_setup_forms(self):
        from django.urls import reverse

        response = self.client.get(reverse("settings_home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<title>تنظیمات | Dia Gallery</title>",
            html=True,
        )
        self.assertContains(response, 'value="business"')
        self.assertContains(response, 'value="sales_channel"')
        self.assertContains(response, 'value="payment_provider"')
        self.assertContains(response, 'value="product_business"')

    def test_settings_can_create_entities_and_assign_product(self):
        from django.urls import reverse
        from dia_core.models import Business, PaymentProvider, SalesChannel

        self.client.raise_request_exception = False
        url = reverse("settings_home")

        response = self.client.post(
            url,
            {
                "action": "business",
                "code": "dia",
                "title": "Dia",
            },
        )
        self.assertEqual(response.status_code, 302)

        business = Business.objects.get(code="dia")

        response = self.client.post(
            url,
            {
                "action": "sales_channel",
                "code": "site",
                "title": "سایت",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(SalesChannel.objects.filter(code="site").exists())

        response = self.client.post(
            url,
            {
                "action": "payment_provider",
                "code": "snapp",
                "title": "اسنپ",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PaymentProvider.objects.filter(code="snapp").exists())

        response = self.client.post(
            url,
            {
                "action": "product_business",
                "product": self.product.id,
                "business": business.id,
            },
        )
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertEqual(self.product.business, business)

class InterBusinessTransferTests(TestCase):
    def setUp(self):
        from dia_core.models import Business, Account

        self.dia = Business.objects.create(
            code="dia-transfer-test",
            title="Dia",
            active=True,
        )
        self.holder = Business.objects.create(
            code="holder-transfer-test",
            title="Holder",
            active=True,
        )
        self.bodyguard = Business.objects.create(
            code="bodyguard-transfer-test",
            title="Bodyguard",
            active=True,
        )

        self.bank = Account.objects.create(
            title="بانک تست انتقال",
            kind=Account.Kind.CASH,
            opening_balance=100_000_000,
            active=True,
        )

    def test_holder_can_fund_dia_without_changing_total_bank_balance(self):
        from dia_core.models import BusinessTransfer
        from dia_core.services import account_balance, business_transfer_position

        before_bank = account_balance(self.bank)

        BusinessTransfer.objects.create(
            date=date(2026, 9, 17),
            from_business=self.holder,
            to_business=self.dia,
            amount=10_000_000,
            note="کمک نقدینگی",
        )

        after_bank = account_balance(self.bank)

        self.assertEqual(before_bank, 100_000_000)
        self.assertEqual(after_bank, 100_000_000)

        holder = business_transfer_position(self.holder)
        dia = business_transfer_position(self.dia)

        self.assertEqual(holder["receivable"], 10_000_000)
        self.assertEqual(holder["payable"], 0)
        self.assertEqual(holder["net"], 10_000_000)

        self.assertEqual(dia["receivable"], 0)
        self.assertEqual(dia["payable"], 10_000_000)
        self.assertEqual(dia["net"], -10_000_000)

    def test_transfer_works_between_any_two_different_businesses(self):
        from dia_core.models import BusinessTransfer

        row = BusinessTransfer.objects.create(
            date=date(2026, 9, 17),
            from_business=self.bodyguard,
            to_business=self.holder,
            amount=5_000_000,
        )

        self.assertEqual(row.from_business, self.bodyguard)
        self.assertEqual(row.to_business, self.holder)
        self.assertEqual(row.amount, 5_000_000)

    def test_reverse_transfer_nets_the_internal_balance(self):
        from dia_core.models import BusinessTransfer
        from dia_core.services import business_transfer_position

        BusinessTransfer.objects.create(
            date=date(2026, 9, 17),
            from_business=self.holder,
            to_business=self.dia,
            amount=10_000_000,
        )
        BusinessTransfer.objects.create(
            date=date(2026, 9, 18),
            from_business=self.dia,
            to_business=self.holder,
            amount=10_000_000,
        )

        holder = business_transfer_position(self.holder)
        dia = business_transfer_position(self.dia)

        self.assertEqual(holder["receivable"], 0)
        self.assertEqual(holder["payable"], 0)
        self.assertEqual(holder["net"], 0)

        self.assertEqual(dia["receivable"], 0)
        self.assertEqual(dia["payable"], 0)
        self.assertEqual(dia["net"], 0)


class FinanceTransferViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from dia_core.models import Business

        self.user = get_user_model().objects.create_user(
            username="finance-transfer-user",
            password="test-pass-123",
        )
        self.client.force_login(self.user)

        self.dia = Business.objects.create(
            code="dia-finance-view",
            title="Dia",
        )
        self.holder = Business.objects.create(
            code="holder-finance-view",
            title="Holder",
        )

    def test_finance_can_create_business_transfer(self):
        from dia_core.models import BusinessTransfer

        response = self.client.post(
            "/finance/",
            {
                "action": "business_transfer",
                "date": "1405/06/26",
                "from_business": self.holder.id,
                "to_business": self.dia.id,
                "amount": "10000000",
                "note": "تامین نقدینگی Dia",
            },
        )

        self.assertEqual(response.status_code, 302)

        row = BusinessTransfer.objects.get()
        self.assertEqual(row.from_business, self.holder)
        self.assertEqual(row.to_business, self.dia)
        self.assertEqual(row.amount, 10_000_000)


class FinanceDashboardTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from dia_core.models import Account, Business, BusinessTransfer

        user = get_user_model().objects.create_user(
            username="finance-dashboard-user",
            password="test-pass-123",
        )
        self.client.force_login(user)

        self.dia = Business.objects.create(code="dia-dashboard", title="Dia")
        self.bodyguard = Business.objects.create(code="bodyguard-dashboard", title="Bodyguard")
        self.holder = Business.objects.create(code="holder-dashboard", title="Holder")

        Account.objects.create(
            title="بانک داشبورد تست",
            kind=Account.Kind.CASH,
            opening_balance=142_918_000,
        )
        Account.objects.create(
            title="بدهی علی داشبورد",
            kind=Account.Kind.PAYABLE,
            business=self.dia,
            opening_balance=64_500_000,
        )
        Account.objects.create(
            title="بدهی آرش داشبورد",
            kind=Account.Kind.PAYABLE,
            business=self.bodyguard,
            opening_balance=87_500_000,
        )
        Account.objects.create(
            title="بدهی مهر داشبورد",
            kind=Account.Kind.PAYABLE,
            business=self.holder,
            opening_balance=102_280_000,
        )
        Account.objects.create(
            title="بیعانه داشبورد",
            kind=Account.Kind.CUSTOMER_DEPOSIT,
            business=self.holder,
            opening_balance=20_000_000,
        )
        Account.objects.create(
            title="طلب داشبورد",
            kind=Account.Kind.RECEIVABLE,
            opening_balance=18_000_000,
        )

        BusinessTransfer.objects.create(
            date=date(2026, 9, 17),
            from_business=self.holder,
            to_business=self.dia,
            amount=10_000_000,
        )

    def test_finance_context_has_summary_and_business_positions(self):
        response = self.client.get("/finance/")

        self.assertEqual(response.status_code, 200)

        summary = response.context["finance_summary"]
        self.assertEqual(summary["cash"], 142_918_000)
        self.assertEqual(summary["payables"], 254_280_000)
        self.assertEqual(summary["customer_deposits"], 20_000_000)
        self.assertEqual(summary["receivables"], 18_000_000)
        self.assertEqual(summary["spendable"], -131_362_000)

        positions = {
            row["business"].code: row
            for row in response.context["business_positions"]
        }

        self.assertEqual(positions["holder-dashboard"]["receivable"], 10_000_000)
        self.assertEqual(positions["holder-dashboard"]["payable"], 0)
        self.assertEqual(positions["dia-dashboard"]["payable"], 10_000_000)


class FinanceTemplateTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from dia_core.models import Business

        user = get_user_model().objects.create_user(
            username="finance-template-user",
            password="test-pass-123",
        )
        self.client.force_login(user)

        Business.objects.create(code="dia-template", title="Dia")
        Business.objects.create(code="holder-template", title="Holder")
        Business.objects.create(code="bodyguard-template", title="Bodyguard")

    def test_finance_page_shows_summary_and_transfer_form(self):
        response = self.client.get("/finance/")

        self.assertContains(response, "پول قابل خرج")
        self.assertContains(response, "انتقال بین بیزنس‌ها")
        self.assertContains(response, 'name="from_business"')
        self.assertContains(response, 'name="to_business"')
        self.assertContains(response, "طلب از بیزنس‌ها")
        self.assertContains(response, "بدهی به بیزنس‌ها")
