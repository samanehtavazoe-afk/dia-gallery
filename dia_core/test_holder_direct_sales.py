from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from . import models, services
from .models import Account, SaleDay


class HolderDirectSaleTests(TestCase):
    def _model(self, name):
        self.assertTrue(hasattr(models, name), f"{name} must exist")
        return getattr(models, name)

    def _service(self):
        self.assertTrue(
            hasattr(services, "record_holder_receipt"),
            "record_holder_receipt must exist",
        )
        return services.record_holder_receipt

    def _order(self, *, total=330000):
        HolderDirectOrder = self._model("HolderDirectOrder")
        return HolderDirectOrder.objects.create(
            date=timezone.localdate(),
            customer_name="مشتری تست",
            quantity_small=1,
            quantity_medium=2,
            quantity_large=3,
            unit_price_small=90000,
            unit_price_medium=100000,
            unit_price_large=110000,
            order_total=total,
        )

    def test_order_stores_three_sizes_and_tracks_remaining_customer_balance(self):
        HolderDirectReceipt = self._model("HolderDirectReceipt")
        order = self._order(total=500000)

        HolderDirectReceipt.objects.create(
            order=order,
            amount=120000,
            receipt_type="deposit",
            recipient="mehr",
            date=timezone.localdate(),
        )
        HolderDirectReceipt.objects.create(
            order=order,
            amount=80000,
            receipt_type="balance",
            recipient="samaneh",
            date=timezone.localdate(),
        )

        self.assertEqual(order.quantity_small, 1)
        self.assertEqual(order.quantity_medium, 2)
        self.assertEqual(order.quantity_large, 3)
        self.assertEqual(order.remaining_balance, 300000)

    def test_samaneh_receipt_increases_cash_once(self):
        order = self._order()
        bank = Account.objects.create(
            title="بانک تست هولدر",
            kind=Account.Kind.CASH,
            opening_balance=1000000,
            active=True,
        )

        receipt = self._service()(
            order=order,
            amount=150000,
            receipt_type="deposit",
            recipient="samaneh",
            date=timezone.localdate(),
        )

        self.assertEqual(services.account_balance(bank), 1150000)
        self.assertEqual(
            bank.entries.filter(reference=f"holder-receipt:{receipt.id}").count(),
            1,
        )

    def test_mehr_receipt_does_not_change_cash_and_is_queryable(self):
        HolderDirectReceipt = self._model("HolderDirectReceipt")
        order = self._order()
        bank = Account.objects.create(
            title="بانک تست هولدر",
            kind=Account.Kind.CASH,
            opening_balance=1000000,
            active=True,
        )

        self._service()(
            order=order,
            amount=200000,
            receipt_type="deposit",
            recipient="mehr",
            date=timezone.localdate(),
        )

        self.assertEqual(services.account_balance(bank), 1000000)
        held_by_mehr = (
            HolderDirectReceipt.objects
            .filter(recipient="mehr")
            .aggregate(v=Sum("amount"))["v"]
            or 0
        )
        self.assertEqual(int(held_by_mehr), 200000)
        self.assertEqual(bank.entries.count(), 0)


class HolderDirectSaleViewTests(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username="holder-direct-view-test",
            password="test-pass-123",
        )
        self.client.force_login(user)
        self.day = SaleDay.objects.create(date=timezone.localdate())
        self.bank = Account.objects.create(
            title="بانک هولدر ویو",
            kind=Account.Kind.CASH,
            opening_balance=1000000,
            active=True,
        )
        self.url = reverse("sale_day", args=[self.day.id])

    def test_holder_mode_shows_dedicated_persian_size_form(self):
        response = self.client.get(self.url, {"mode": "holder"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "نام مشتری")
        self.assertContains(response, "سایز کوچک")
        self.assertContains(response, "سایز متوسط")
        self.assertContains(response, "سایز بزرگ")
        self.assertContains(response, "مبلغ دریافتی الان")
        self.assertContains(response, "سمانه")
        self.assertContains(response, "مهر")
        self.assertNotContains(response, "کالاهای فاکتور")

    def test_holder_post_creates_order_receipt_and_updates_cash_for_samaneh(self):
        HolderDirectOrder = models.HolderDirectOrder
        HolderDirectReceipt = models.HolderDirectReceipt

        response = self.client.post(
            self.url,
            {
                "mode": "holder",
                "customer_name": "مشتری حضوری",
                "quantity_small": "2",
                "quantity_medium": "1",
                "quantity_large": "3",
                "unit_price_small": "90000",
                "unit_price_medium": "100000",
                "unit_price_large": "110000",
                "amount_received": "200000",
                "receipt_type": "deposit",
                "recipient": "samaneh",
                "note": "بیعانه سفارش هولدر",
            },
        )

        self.assertEqual(response.status_code, 302)
        order = HolderDirectOrder.objects.get()
        receipt = HolderDirectReceipt.objects.get(order=order)
        self.assertEqual(order.date, self.day.date)
        self.assertEqual(order.customer_name, "مشتری حضوری")
        self.assertEqual(order.quantity_small, 2)
        self.assertEqual(order.quantity_medium, 1)
        self.assertEqual(order.quantity_large, 3)
        self.assertEqual(order.order_total, 610000)
        self.assertEqual(receipt.amount, 200000)
        self.assertEqual(receipt.recipient, "samaneh")
        self.assertEqual(order.remaining_balance, 410000)
        self.assertEqual(services.account_balance(self.bank), 1200000)
