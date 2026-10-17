import uuid
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
class BankAccount(models.Model):
    class AccountType(models.TextChoices):
        SAVINGS="savings","Savings"
        CURRENT="current","Current"
    class Status(models.TextChoices):
        ACTIVE="active","Active"
        BLOCKED="blocked","Blocked"
        CLOSED="closed","Closed"
    owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="bank_accounts")
    account_number=models.CharField(max_length=20,unique=True,editable=False)
    account_type=models.CharField(max_length=10,choices=AccountType.choices)
    balance=models.DecimalField(max_digits=14,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    status=models.CharField(max_length=10,choices=Status.choices,default=Status.ACTIVE)
    created_at=models.DateTimeField(auto_now_add=True)
    def save(self,*args,**kwargs):
        if not self.account_number:
            while True:
                candidate=uuid.uuid4().hex[:12].upper()
                if not BankAccount.objects.filter(account_number=candidate).exists():
                    self.account_number=candidate; break
        super().save(*args,**kwargs)
    def __str__(self): return f"{self.account_number} ({self.owner})"
class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT="deposit","Deposit"
        WITHDRAWAL="withdrawal","Withdrawal"
        TRANSFER_SENT="transfer_sent","Transfer sent"
        TRANSFER_RECEIVED="transfer_received","Transfer received"
    reference=models.UUIDField(default=uuid.uuid4,unique=True,editable=False)
    transaction_type=models.CharField(max_length=20,choices=TransactionType.choices)
    amount=models.DecimalField(max_digits=14,decimal_places=2,validators=[MinValueValidator(0.01)])
    account=models.ForeignKey(BankAccount,on_delete=models.PROTECT,related_name="transactions")
    related_account=models.ForeignKey(BankAccount,on_delete=models.PROTECT,null=True,blank=True,related_name="related_transactions")
    description=models.CharField(max_length=255,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=["-created_at"]
        indexes=[models.Index(fields=["transaction_type","created_at"])]
    def __str__(self): return f"{self.transaction_type}: {self.amount} ({self.reference})"
