from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Business,
    Color,
    Product,
    ProductVariant,
    SaleDay,
    SalesChannel,
    Size,
)


class SiteMultibusinessSalesTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="site-multi-test",
            password="test-pass-123",
        )
        self.client.force_login(user)

        self.day = SaleDay.objects.create(date=timezone.localdate())
        SalesChannel.objects.create(
            code="site",
            title="سایت",
            active=True,
        )

        size = Size.objects.create(name="M")
        color = Color.objects.create(name="مشکی")

        for code, title in (
            ("DIA-1", "محصول دیا"),
            ("BODY-1", "محصول بادیگارد"),
            ("HOLDER-1", "قالب نوبنیان"),
        ):
            business = Business.objects.create(
                code=code.lower(),
                title=title,
                active=True,
            )
            product = Product.objects.create(
                code=code,
                title=title,
                business=business,
                active=True,
            )
            ProductVariant.objects.create(
                product=product,
                size=size,
                color=color,
                default_sale_price=100000,
                unit_cost=50000,
                active=True,
            )

    def test_site_mode_shows_products_from_all_businesses(self):
        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "site"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DIA-1")
        self.assertContains(response, "BODY-1")
        self.assertContains(response, "HOLDER-1")

    def test_site_invoice_can_be_business_neutral(self):
        from .models import SaleOrder

        self.assertTrue(
            SaleOrder._meta.get_field("business").null
        )

    def test_site_invoice_can_save_lines_from_multiple_businesses(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        dia_variant = ProductVariant.objects.get(product__code="DIA-1")
        body_variant = ProductVariant.objects.get(product__code="BODY-1")

        StockBalance.objects.create(
            variant=dia_variant,
            location=location,
            qty=100,
        )
        StockBalance.objects.create(
            variant=body_variant,
            location=location,
            qty=100,
        )

        self.client.raise_request_exception = False

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": "",
                "shipping_collected": "0",
                "shipping_cost": "0",
                f"qty_{dia_variant.id}": "2",
                f"price_{dia_variant.id}": "120000",
                f"qty_{body_variant.id}": "3",
                f"price_{body_variant.id}": "150000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        self.assertIsNone(order.business)

        lines = {
            line.variant.product.code: line
            for line in order.lines.select_related(
                "variant__product",
                "business",
            )
        }

        self.assertEqual(set(lines), {"DIA-1", "BODY-1"})
        self.assertEqual(lines["DIA-1"].business, dia_variant.product.business)
        self.assertEqual(lines["BODY-1"].business, body_variant.product.business)

        self.assertEqual(
            StockBalance.objects.get(
                variant=dia_variant,
                location=location,
            ).qty,
            98,
        )
        self.assertEqual(
            StockBalance.objects.get(
                variant=body_variant,
                location=location,
            ).qty,
            97,
        )

    def test_site_mode_renders_simplified_sales_form(self):
        business = Business.objects.get(code="dia-1")
        business.title = "برند DIA"
        business.save(update_fields=["title"])

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "site"},
        )

        self.assertEqual(response.status_code, 200)

        # چیزهایی که باید باشند
        self.assertContains(response, 'name="payment_provider"')
        self.assertContains(response, 'name="shipping_cost"')
        self.assertContains(response, "برند DIA")
        self.assertContains(response, 'name="qty_')
        self.assertContains(response, 'name="price_')

        # چیزهای اضافی که در فروش سایت نباید دیده شوند
        self.assertNotContains(response, 'name="business"')
        self.assertNotContains(response, 'name="sales_channel"')
        self.assertNotContains(response, 'name="payment_status"')
        self.assertNotContains(response, 'name="external_reference"')
        self.assertNotContains(response, 'name="expected_settlement_date"')
        self.assertNotContains(response, 'name="settled_date"')
        self.assertNotContains(response, 'name="shipping_collected"')
        self.assertNotContains(response, 'name="provider_fee_collected"')

    def test_editing_site_invoice_preserves_line_businesses_and_adjusts_stock(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        dia_variant = ProductVariant.objects.get(product__code="DIA-1")
        body_variant = ProductVariant.objects.get(product__code="BODY-1")

        StockBalance.objects.create(
            variant=dia_variant,
            location=location,
            qty=100,
        )
        StockBalance.objects.create(
            variant=body_variant,
            location=location,
            qty=100,
        )

        create_response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": "",
                "shipping_cost": "0",
                f"qty_{dia_variant.id}": "2",
                f"price_{dia_variant.id}": "120000",
                f"qty_{body_variant.id}": "3",
                f"price_{body_variant.id}": "150000",
            },
        )
        self.assertEqual(create_response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)

        self.client.raise_request_exception = False

        edit_response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "order_id": str(order.id),
                "payment_provider": "",
                "shipping_cost": "0",
                f"qty_{dia_variant.id}": "5",
                f"price_{dia_variant.id}": "125000",
                f"qty_{body_variant.id}": "1",
                f"price_{body_variant.id}": "155000",
            },
        )

        self.assertEqual(edit_response.status_code, 302)

        order.refresh_from_db()
        self.assertIsNone(order.business)

        lines = {
            line.variant.product.code: line
            for line in order.lines.select_related(
                "variant__product__business",
                "business",
            )
        }

        self.assertEqual(lines["DIA-1"].business, dia_variant.product.business)
        self.assertEqual(lines["BODY-1"].business, body_variant.product.business)
        self.assertEqual(lines["DIA-1"].quantity, 5)
        self.assertEqual(lines["BODY-1"].quantity, 1)

        self.assertEqual(
            StockBalance.objects.get(
                variant=dia_variant,
                location=location,
            ).qty,
            95,
        )
        self.assertEqual(
            StockBalance.objects.get(
                variant=body_variant,
                location=location,
            ).qty,
            99,
        )

    def test_site_sale_rejects_quantity_above_available_stock(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        balance = StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=2,
        )

        with self.assertRaises(ValueError):
            self.client.post(
                reverse("sale_day", args=[self.day.id]),
                {
                    "mode": "site",
                    "payment_provider": "",
                    "shipping_cost": "0",
                    f"qty_{variant.id}": "5",
                    f"price_{variant.id}": "120000",
                },
            )

        balance.refresh_from_db()
        self.assertEqual(balance.qty, 2)

        self.assertFalse(
            SaleOrder.objects.filter(day=self.day).exists()
        )

    def test_site_digipay_fee_and_payment_status_are_automatic(self):
        from .models import (
            AppSetting,
            PaymentProvider,
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        digipay = PaymentProvider.objects.create(
            code="digipay",
            title="DigiPay",
            active=True,
        )

        AppSetting.objects.create(
            key="digipay_commission_percent",
            value="10",
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": str(digipay.id),
                "shipping_cost": "0",
                f"qty_{variant.id}": "2",
                f"price_{variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        line = order.lines.get(variant=variant)

        self.assertEqual(order.payment_provider, digipay)
        self.assertEqual(
            order.payment_status,
            SaleOrder.PaymentStatus.PENDING,
        )

        # 10% of 100,000
        self.assertEqual(
            line.provider_fee_unit_snapshot,
            10000,
        )

        # 2 items × 10,000 fee
        self.assertEqual(
            order.provider_fee_collected,
            20000,
        )

    def test_site_summary_shows_financial_breakdown_and_net_receivable(self):
        from .models import (
            AppSetting,
            PaymentProvider,
            ProductVariant,
            SaleOrder,
            StockBalance,
            StockLocation,
        )

        digipay = PaymentProvider.objects.create(
            code="digipay",
            title="DigiPay",
            active=True,
        )

        AppSetting.objects.create(
            key="digipay_commission_percent",
            value="10",
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": str(digipay.id),
                "shipping_cost": "15000",
                f"qty_{variant.id}": "2",
                f"price_{variant.id}": "100000",
            },
        )

        order = SaleOrder.objects.get(day=self.day)

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "order": order.id,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "فروش ناخالص")
        self.assertContains(response, "کل کارمزدها")
        self.assertContains(response, "خالص دریافتی / طلب درگاه")
        self.assertContains(response, "هزینه پست")
        self.assertContains(response, "بهای کالا")
        self.assertContains(response, "سود فاکتور")

        self.assertIn("net_receivable", response.context["total"])

    def test_site_invoice_shows_provider_settlement_rule(self):
        from .models import AppSetting, PaymentProvider, SaleOrder

        digipay = PaymentProvider.objects.create(
            code="digipay",
            title="DigiPay Settlement",
            active=True,
        )

        AppSetting.objects.create(
            key="digipay_settlement_rule",
            value="تسویه روز ۷ هر ماه",
            label="قاعده تسویه دیجی‌پی",
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "payment_provider": str(digipay.id),
            },
        )

        order = SaleOrder.objects.get(day=self.day)

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "site",
                "order": order.id,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "قاعده تسویه")
        self.assertContains(response, "تسویه روز ۷ هر ماه")

    def test_basalam_mode_shows_products_from_all_businesses(self):
        SalesChannel.objects.create(
            code="basalam",
            title="باسلام",
            active=True,
        )

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "basalam"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DIA-1")
        self.assertContains(response, "BODY-1")
        self.assertContains(response, "HOLDER-1")

    def test_basalam_invoice_preserves_each_lines_real_business(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            SalesChannel,
            StockBalance,
            StockLocation,
        )

        basalam, _ = SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={
                "title": "باسلام",
                "active": True,
            },
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        dia_variant = ProductVariant.objects.get(product__code="DIA-1")
        holder_variant = ProductVariant.objects.get(product__code="HOLDER-1")

        StockBalance.objects.create(
            variant=dia_variant,
            location=location,
            qty=10,
        )
        StockBalance.objects.create(
            variant=holder_variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "business": str(dia_variant.product.business_id),
                f"qty_{dia_variant.id}": "2",
                f"price_{dia_variant.id}": "100000",
                f"qty_{holder_variant.id}": "3",
                f"price_{holder_variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        lines = {
            line.variant.product.code: line
            for line in order.lines.select_related(
                "variant__product",
                "business",
            )
        }

        self.assertEqual(
            lines["DIA-1"].business_id,
            dia_variant.product.business_id,
        )
        self.assertEqual(
            lines["HOLDER-1"].business_id,
            holder_variant.product.business_id,
        )

    def test_basalam_invoice_does_not_require_business_selection(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            SalesChannel,
            StockBalance,
            StockLocation,
        )

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        dia_variant = ProductVariant.objects.get(product__code="DIA-1")
        StockBalance.objects.create(
            variant=dia_variant,
            location=location,
            qty=10,
        )

        self.client.raise_request_exception = False

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                f"qty_{dia_variant.id}": "1",
                f"price_{dia_variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        line = order.lines.get()

        self.assertEqual(
            line.business_id,
            dia_variant.product.business_id,
        )

    def test_basalam_form_hides_business_selector(self):
        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "basalam"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="business"')

    def test_basalam_invoice_saves_installment_payment_type(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            SalesChannel,
            StockBalance,
            StockLocation,
        )

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")
        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                f"qty_{variant.id}": "1",
                f"price_{variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        self.assertEqual(
            order.basalam_payment_type,
            "installment",
        )

    def test_basalam_form_shows_cash_and_installment_payment_types(self):
        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "basalam"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="basalam_payment_type"')
        self.assertContains(response, 'value="cash"')
        self.assertContains(response, 'value="installment"')
        self.assertContains(response, "نقدی")
        self.assertContains(response, "اقساطی")

    def test_basalam_form_shows_cash_and_installment_payment_types(self):
        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "basalam"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="basalam_payment_type"')
        self.assertContains(response, 'value="cash"')
        self.assertContains(response, 'value="installment"')
        self.assertContains(response, "نقدی")
        self.assertContains(response, "اقساطی")

    def test_basalam_installment_plan_matches_reference_example(self):
        from .services import basalam_installment_plan

        plan = basalam_installment_plan(1000000)

        self.assertEqual(plan["down_payment"], 250000)
        self.assertEqual(plan["financed_amount"], 750000)
        self.assertEqual(plan["installment_count"], 2)
        self.assertEqual(plan["installment_amount"], 394800)
        self.assertEqual(plan["installments_total"], 789600)
        self.assertEqual(plan["total_payable"], 1039600)
        self.assertEqual(plan["price_increase"], 39600)

    def test_basalam_installment_sale_uses_final_payable_for_fee_and_metrics(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            SalesChannel,
            StockBalance,
            StockLocation,
        )
        from .services import sale_metrics

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")

        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                f"qty_{variant.id}": "1",
                f"price_{variant.id}": "1000000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        line = order.lines.get()

        self.assertEqual(line.base_sale_price, 1000000)
        self.assertEqual(line.sale_price, 1000000)
        self.assertEqual(line.basalam_installment_increase, 39600)
        self.assertEqual(line.channel_fee_unit_snapshot, 145544)

        metrics = sale_metrics(line)
        self.assertEqual(metrics["gross"], 1039600)
        self.assertEqual(metrics["channel_fee"], 145544)

    def test_basalam_installment_order_saves_payment_snapshot_excluding_shipping(self):
        from .models import (
            ProductVariant,
            SaleOrder,
            SalesChannel,
            StockBalance,
            StockLocation,
        )

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام", "active": True},
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")
        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                "shipping_cost": "160000",
                f"qty_{variant.id}": "1",
                f"price_{variant.id}": "1000000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)

        self.assertEqual(order.basalam_down_payment, 250000)
        self.assertEqual(order.basalam_installment_count, 2)
        self.assertEqual(order.basalam_installment_amount, 394800)
        self.assertEqual(order.basalam_price_increase, 39600)
        self.assertEqual(order.basalam_total_payable, 1039600)

    def test_basalam_installment_multi_quantity_fee_uses_exact_final_line_total(self):
        from .models import SaleLine, StockBalance, StockLocation
        from .services import sale_metrics
        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "باسلام"},
        )

        location = StockLocation.objects.create(
            key="main",
            title="انبار اصلی",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")
        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
         )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                f"qty_{variant.id}": "3",
                f"price_{variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        line = SaleLine.objects.get(
            order__day=self.day,
            variant=variant,
        )
        metrics = sale_metrics(line)

        self.assertEqual(line.basalam_installment_increase, 11880)
        self.assertEqual(metrics["gross"], 311880)
        self.assertEqual(metrics["channel_fee"], 43663)

    def test_basalam_edit_installment_to_cash_clears_installment_values(self):
        from .models import SaleLine, SaleOrder, StockBalance, StockLocation
        from .services import sale_metrics

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "Basalam"},
        )

        location = StockLocation.objects.create(
            key="main",
            title="Main",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")
        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                f"qty_{variant.id}": "1",
                f"price_{variant.id}": "100000",
            },
        )
        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "order_id": str(order.id),
                "basalam_payment_type": "cash",
                f"qty_{variant.id}": "1",
                f"price_{variant.id}": "100000",
            },
        )
        self.assertEqual(response.status_code, 302)

        order.refresh_from_db()
        line = SaleLine.objects.get(order=order, variant=variant)
        metrics = sale_metrics(line)

        self.assertEqual(order.basalam_down_payment, 0)
        self.assertEqual(order.basalam_installment_count, 0)
        self.assertEqual(order.basalam_installment_amount, 0)
        self.assertEqual(order.basalam_price_increase, 0)
        self.assertEqual(order.basalam_total_payable, 0)
        self.assertEqual(line.basalam_installment_increase, 0)
        self.assertEqual(metrics["gross"], 100000)
        self.assertEqual(metrics["channel_fee"], 14000)
    def test_basalam_installment_mixed_businesses_use_correct_commission_rates(self):
        from .models import SaleOrder, StockBalance, StockLocation
        from .services import sale_metrics

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "Basalam", "active": True},
        )

        location = StockLocation.objects.create(
            key="main",
            title="Main",
            active=True,
        )

        dia = ProductVariant.objects.get(product__code="DIA-1")
        body = ProductVariant.objects.get(product__code="BODY-1")
        holder = ProductVariant.objects.get(product__code="HOLDER-1")

        dia.product.business.code = "dia"
        dia.product.business.save(update_fields=["code"])

        body.product.business.code = "bodyguard"
        body.product.business.save(update_fields=["code"])

        holder.product.business.code = "holder"
        holder.product.business.save(update_fields=["code"])

        for variant in (dia, body, holder):
            StockBalance.objects.create(
                variant=variant,
                location=location,
                qty=20,
            )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                f"qty_{dia.id}": "3",
                f"price_{dia.id}": "100000",
                f"qty_{body.id}": "2",
                f"price_{body.id}": "150000",
                f"qty_{holder.id}": "2",
                f"price_{holder.id}": "200000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        lines = {
            line.variant.product.code: line
            for line in order.lines.select_related("variant__product")
        }

        self.assertEqual(order.basalam_price_increase, 39600)
        self.assertEqual(order.basalam_total_payable, 1039600)

        self.assertEqual(lines["DIA-1"].basalam_installment_increase, 11880)
        self.assertEqual(lines["BODY-1"].basalam_installment_increase, 11880)
        self.assertEqual(lines["HOLDER-1"].basalam_installment_increase, 15840)

        self.assertEqual(sale_metrics(lines["DIA-1"])["channel_fee"], 43663)
        self.assertEqual(sale_metrics(lines["BODY-1"])["channel_fee"], 43663)
        self.assertEqual(sale_metrics(lines["HOLDER-1"])["channel_fee"], 43663)
    def test_basalam_edit_form_keeps_installment_selected(self):
        from .models import SaleOrder

        channel, _ = SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "Basalam", "active": True},
        )

        order = SaleOrder.objects.create(
            day=self.day,
            sales_channel=channel,
            basalam_payment_type="installment",
        )

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "order": str(order.id),
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="installment" selected')
    def test_basalam_installment_edit_form_shows_installment_summary(self):
        from .models import SaleOrder

        channel, _ = SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "Basalam", "active": True},
        )

        order = SaleOrder.objects.create(
            day=self.day,
            sales_channel=channel,
            basalam_payment_type="installment",
            basalam_down_payment=250000,
            basalam_installment_count=2,
            basalam_installment_amount=394800,
            basalam_price_increase=39600,
            basalam_total_payable=1039600,
        )

        response = self.client.get(
            reverse("sale_day", args=[self.day.id]),
            {"mode": "basalam", "order": str(order.id)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="basalam-installment-summary"')
        self.assertContains(response, "250000")
        self.assertContains(response, "394800")
        self.assertContains(response, "39600")
        self.assertContains(response, "1039600")
    def test_basalam_installment_platform_receivable_uses_final_amount_and_exact_fee(self):
        from .models import SaleOrder, StockBalance, StockLocation
        from .services import platform_receivable_totals

        SalesChannel.objects.get_or_create(
            code="basalam",
            defaults={"title": "Basalam", "active": True},
        )

        location = StockLocation.objects.create(
            key="main",
            title="Main",
            active=True,
        )

        variant = ProductVariant.objects.get(product__code="DIA-1")
        StockBalance.objects.create(
            variant=variant,
            location=location,
            qty=10,
        )

        response = self.client.post(
            reverse("sale_day", args=[self.day.id]),
            {
                "mode": "basalam",
                "basalam_payment_type": "installment",
                f"qty_{variant.id}": "3",
                f"price_{variant.id}": "100000",
            },
        )

        self.assertEqual(response.status_code, 302)

        order = SaleOrder.objects.get(day=self.day)
        self.assertEqual(
            order.payment_status,
            SaleOrder.PaymentStatus.PENDING,
        )

        totals = platform_receivable_totals()
        self.assertEqual(totals["basalam"], 268217)
