from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient
from apps.accounts.models import Role
from apps.alerts.models import Alert
from apps.branches.models import Branch, DiningTable
from apps.inventory.models import Ingredient, RecipeBOM, StockTransaction
from apps.menu.models import Category, MenuItem
from apps.payments.models import Payment, PaymentProof

User = get_user_model()


ONE_PIXEL_PNG = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\x0dIDAT\x08\xd7c\xf8\xcf\xc0\xf0\x1f\x00\x05\x00\x01\xff"
    b"\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
)


class WaiterOrderFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        waiter_role = Role.objects.create(role_name="WAITER")
        self.admin_role = Role.objects.create(role_name="SYSTEM_ADMIN")
        self.waiter = User.objects.create_user(
            username="waiter1", password="Pass12345!", role=waiter_role, full_name="Lema", branch=None
        )
        self.admin = User.objects.create_user(
            username="admin1", password="Pass12345!", role=self.admin_role, full_name="Admin", is_staff=True
        )
        self.branch = Branch.objects.create(name="Main Branch", phone="0911000000")
        self.waiter.branch = self.branch
        self.waiter.save(update_fields=["branch"])
        self.table = DiningTable.objects.create(branch=self.branch, table_number="T1", capacity=4)
        self.category = Category.objects.create(name="Food", meal_period="ALL_DAY")
        self.item = MenuItem.objects.create(
            category=self.category, name="Burger", selling_price=Decimal("200.00"), kitchen_station="HOT"
        )
        self.ingredient = Ingredient.objects.create(
            sku="BUN-001", name="Burger Bun", unit_of_measure="pcs", current_stock=Decimal("10"),
            reorder_level=Decimal("8"), unit_cost=Decimal("20"), branch=self.branch
        )
        RecipeBOM.objects.create(item=self.item, ingredient=self.ingredient, required_qty=Decimal("1"), unit="pcs")
        self.client.force_authenticate(user=self.waiter)

    def create_order(self):
        return self.client.post(
            "/api/orders/",
            {
                "branch_id": self.branch.pk,
                "table_id": self.table.pk,
                "items": [{"menu_item_id": self.item.pk, "quantity": "2"}],
            },
            format="json",
        )

    def test_create_order_matches_ui_ordered_state_and_deducts_stock(self):
        response = self.create_order()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "SENT")
        self.assertEqual(response.data["ui_status"], "ORDERED")
        self.assertEqual(Ingredient.objects.get(pk=self.ingredient.pk).current_stock, Decimal("8.0000"))
        self.assertEqual(StockTransaction.objects.count(), 1)
        self.assertEqual(DiningTable.objects.get(pk=self.table.pk).status, DiningTable.Status.OCCUPIED)

    def test_cancel_releases_table(self):
        order_id = self.create_order().data["order_id"]
        response = self.client.post(f"/api/orders/{order_id}/cancel/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["ui_status"], "CANCELLED")
        self.assertEqual(DiningTable.objects.get(pk=self.table.pk).status, DiningTable.Status.FREE)

    def test_cancel_reverses_stock_with_compensating_adjustment(self):
        order_id = self.create_order().data["order_id"]
        response = self.client.post(f"/api/orders/{order_id}/cancel/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Ingredient.objects.get(pk=self.ingredient.pk).current_stock, Decimal("10.0000"))
        self.assertEqual(StockTransaction.objects.filter(order_id=order_id).count(), 2)
        self.assertEqual(StockTransaction.objects.filter(order_id=order_id, txn_type=StockTransaction.TxnType.ADJUSTMENT).count(), 1)
        self.assertFalse(Alert.objects.filter(ingredient=self.ingredient, alert_type="LOW_STOCK", ack_status=Alert.AckStatus.OPEN).exists())

    def test_pending_digital_payment_blocks_cancel(self):
        order_id = self.create_order().data["order_id"]
        response = self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {"method": "CBE_BIRR", "proof_image": SimpleUploadedFile("payment.png", ONE_PIXEL_PNG, content_type="image/png")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        cancel = self.client.post(f"/api/orders/{order_id}/cancel/")
        self.assertEqual(cancel.status_code, 400)

    def test_cash_pay_then_complete(self):
        order_id = self.create_order().data["order_id"]
        response = self.client.post(f"/api/payments/orders/{order_id}/pay/", {"method": "CASH"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["payment"]["status"], "SUCCESS")
        self.assertEqual(response.data["order"]["ui_status"], "PAID")
        finished = self.client.post(f"/api/orders/{order_id}/complete/")
        self.assertEqual(finished.status_code, 200)
        self.assertEqual(finished.data["order"]["status"], "CLOSED")
        self.assertEqual(finished.data["order"]["ui_status"], "COMPLETED")
        self.assertEqual(DiningTable.objects.get(pk=self.table.pk).status, DiningTable.Status.FREE)

    def test_digital_payment_requires_screenshot(self):
        order_id = self.create_order().data["order_id"]
        response = self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {"method": "CBE_BIRR"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_cbe_payment_requires_screenshot_and_waits_for_admin(self):
        order_id = self.create_order().data["order_id"]
        response = self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {
                "method": "CBE_BIRR",
                "proof_image": SimpleUploadedFile("payment.png", ONE_PIXEL_PNG, content_type="image/png"),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["payment"]["status"], "PENDING")
        self.assertEqual(response.data["payment_action"], "AWAITING_ADMIN_VERIFICATION")
        proof = PaymentProof.objects.get(payment__order_id=order_id)
        self.assertEqual(proof.verification_status, PaymentProof.VerificationStatus.PENDING)

        self.client.force_authenticate(user=self.admin)
        approve = self.client.post(f"/api/payments/proofs/{proof.pk}/approve/")
        self.assertEqual(approve.status_code, 200)
        self.assertEqual(approve.data["payment"]["status"], "SUCCESS")
        self.assertEqual(approve.data["proof"]["verification_status"], "APPROVED")

    def test_waiter_cannot_approve_payment_proof(self):
        order_id = self.create_order().data["order_id"]
        self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {"method": "CBE_BIRR", "proof_image": SimpleUploadedFile("payment.png", ONE_PIXEL_PNG, content_type="image/png")},
            format="multipart",
        )
        proof = PaymentProof.objects.get(payment__order_id=order_id)
        response = self.client.post(f"/api/payments/proofs/{proof.pk}/approve/")
        self.assertEqual(response.status_code, 400)

    def test_cbe_payment_can_be_rejected_then_resubmitted(self):
        order_id = self.create_order().data["order_id"]
        first = self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {"method": "CBE_BIRR", "proof_image": SimpleUploadedFile("payment1.png", ONE_PIXEL_PNG, content_type="image/png")},
            format="multipart",
        )
        proof = PaymentProof.objects.get(payment__order_id=order_id)
        self.client.force_authenticate(user=self.admin)
        rejected = self.client.post(f"/api/payments/proofs/{proof.pk}/reject/", {"note": "Amount is not readable."}, format="json")
        self.assertEqual(rejected.status_code, 200)
        self.assertEqual(rejected.data["payment"]["status"], "FAILED")

        self.client.force_authenticate(user=self.waiter)
        second = self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {"method": "CBE_BIRR", "proof_image": SimpleUploadedFile("payment2.png", ONE_PIXEL_PNG, content_type="image/png")},
            format="multipart",
        )
        self.assertEqual(second.status_code, 201)
        self.assertEqual(Payment.objects.filter(order_id=order_id, status=Payment.Status.PENDING).count(), 1)

    def test_double_pending_digital_pay_is_rejected(self):
        order_id = self.create_order().data["order_id"]
        payload = {"method": "CBE_BIRR", "proof_image": SimpleUploadedFile("payment.png", ONE_PIXEL_PNG, content_type="image/png")}
        self.client.post(f"/api/payments/orders/{order_id}/pay/", payload, format="multipart")
        response = self.client.post(
            f"/api/payments/orders/{order_id}/pay/",
            {"method": "CBE_BIRR", "proof_image": SimpleUploadedFile("payment2.png", ONE_PIXEL_PNG, content_type="image/png")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Payment.objects.filter(order_id=order_id, status=Payment.Status.PENDING).count(), 1)

    def test_low_stock_alert_is_created(self):
        self.create_order()
        self.assertTrue(Alert.objects.filter(ingredient=self.ingredient, alert_type="LOW_STOCK").exists())
