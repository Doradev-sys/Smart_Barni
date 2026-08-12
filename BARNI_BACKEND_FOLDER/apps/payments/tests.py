from django.test import TestCase


class PaymentModuleSmokeTests(TestCase):
    def test_module_imports(self):
        from apps.payments.models import Payment, PaymentProof
        self.assertTrue(Payment)
        self.assertTrue(PaymentProof)
