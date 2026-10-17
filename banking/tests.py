from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import BankAccount,Transaction
User=get_user_model()
class BankAPITests(APITestCase):
    def setUp(self):
        self.user=User.objects.create_user(username="alice",password="StrongPass123!")
        self.other=User.objects.create_user(username="bob",password="StrongPass123!")
        self.account=BankAccount.objects.create(owner=self.user,account_type="savings",balance=Decimal("100.00"))
        self.other_account=BankAccount.objects.create(owner=self.other,account_type="current",balance=Decimal("50.00"))
        self.client.force_authenticate(self.user)
    def test_cannot_view_other_account(self):
        r=self.client.get(f"/api/accounts/{self.other_account.id}/"); self.assertEqual(r.status_code,404)
    def test_deposit(self):
        r=self.client.post("/api/transactions/deposit/",{"account_id":self.account.id,"amount":"25.00"},format="json")
        self.assertEqual(r.status_code,201); self.account.refresh_from_db(); self.assertEqual(self.account.balance,Decimal("125.00"))
    def test_insufficient_withdrawal(self):
        r=self.client.post("/api/transactions/withdraw/",{"account_id":self.account.id,"amount":"200.00"},format="json")
        self.assertEqual(r.status_code,400); self.account.refresh_from_db(); self.assertEqual(self.account.balance,Decimal("100.00"))
    def test_transfer_updates_both_balances(self):
        r=self.client.post("/api/transactions/transfer/",{"from_account_id":self.account.id,"to_account_number":self.other_account.account_number,"amount":"30.00"},format="json")
        self.assertEqual(r.status_code,201); self.account.refresh_from_db(); self.other_account.refresh_from_db()
        self.assertEqual(self.account.balance,Decimal("70.00")); self.assertEqual(self.other_account.balance,Decimal("80.00"))
        self.assertEqual(Transaction.objects.filter(transaction_type__in=["transfer_sent","transfer_received"]).count(),2)
    def test_zero_deposit_rejected(self):
        r=self.client.post("/api/transactions/deposit/",{"account_id":self.account.id,"amount":"0"},format="json"); self.assertEqual(r.status_code,400)
