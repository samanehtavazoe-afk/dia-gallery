from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from . import models, services
from .models import Account


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
