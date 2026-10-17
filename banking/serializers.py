from decimal import Decimal
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from .models import BankAccount, Transaction
User=get_user_model()
class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    class Meta:
        model=User
        fields=["id","username","email","first_name","last_name","password"]
    def create(self,validated_data): return User.objects.create_user(**validated_data)
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=["id","username","email","first_name","last_name"]
        read_only_fields=["id","username","email"]
class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model=BankAccount
        fields=["id","account_number","account_type","balance","status","created_at"]
        read_only_fields=["id","account_number","balance","status","created_at"]
class TransactionSerializer(serializers.ModelSerializer):
    account_number=serializers.CharField(source="account.account_number",read_only=True)
    related_account_number=serializers.CharField(source="related_account.account_number",read_only=True,allow_null=True)
    class Meta:
        model=Transaction
        fields=["id","reference","transaction_type","amount","account","account_number","related_account","related_account_number","description","created_at"]
        read_only_fields=fields
class AccountAmountSerializer(serializers.Serializer):
    account_id=serializers.IntegerField()
    amount=serializers.DecimalField(max_digits=14,decimal_places=2,min_value=Decimal("0.01"))
    description=serializers.CharField(required=False,allow_blank=True,max_length=255)
    def validate_account_id(self,value):
        if not BankAccount.objects.filter(pk=value,owner=self.context["request"].user,status="active").exists():
            raise serializers.ValidationError("Active account not found for this customer.")
        return value
class DepositSerializer(AccountAmountSerializer):
    def create(self,data):
        with transaction.atomic():
            account=BankAccount.objects.select_for_update().get(pk=data["account_id"],owner=self.context["request"].user)
            account.balance+=data["amount"]; account.save(update_fields=["balance"])
            return Transaction.objects.create(transaction_type="deposit",amount=data["amount"],account=account,description=data.get("description",""))
class WithdrawalSerializer(AccountAmountSerializer):
    def create(self,data):
        with transaction.atomic():
            account=BankAccount.objects.select_for_update().get(pk=data["account_id"],owner=self.context["request"].user)
            if account.balance<data["amount"]: raise serializers.ValidationError({"amount":"Insufficient funds."})
            account.balance-=data["amount"]; account.save(update_fields=["balance"])
            return Transaction.objects.create(transaction_type="withdrawal",amount=data["amount"],account=account,description=data.get("description",""))
class TransferSerializer(serializers.Serializer):
    from_account_id=serializers.IntegerField()
    to_account_number=serializers.CharField(max_length=20)
    amount=serializers.DecimalField(max_digits=14,decimal_places=2,min_value=Decimal("0.01"))
    description=serializers.CharField(required=False,allow_blank=True,max_length=255)
    def validate(self,attrs):
        user=self.context["request"].user
        sender=BankAccount.objects.filter(pk=attrs["from_account_id"],owner=user,status="active").first()
        receiver=BankAccount.objects.filter(account_number=attrs["to_account_number"],status="active").first()
        if not sender: raise serializers.ValidationError({"from_account_id":"Active sender account not found."})
        if not receiver: raise serializers.ValidationError({"to_account_number":"Active receiver account not found."})
        if sender.pk==receiver.pk: raise serializers.ValidationError({"to_account_number":"Cannot transfer to the same account."})
        attrs["sender_id"]=sender.pk; attrs["receiver_id"]=receiver.pk
        return attrs
    def create(self,data):
        amount=data["amount"]
        with transaction.atomic():
            accounts={a.pk:a for a in BankAccount.objects.select_for_update().filter(pk__in=[data["sender_id"],data["receiver_id"]]).order_by("pk")}
            sender,receiver=accounts[data["sender_id"]],accounts[data["receiver_id"]]
            if sender.status!="active" or receiver.status!="active": raise serializers.ValidationError("Both accounts must be active.")
            if sender.balance<amount: raise serializers.ValidationError({"amount":"Insufficient funds."})
            sender.balance-=amount; receiver.balance+=amount
            sender.save(update_fields=["balance"]); receiver.save(update_fields=["balance"])
            desc=data.get("description","")
            tx=Transaction.objects.create(transaction_type="transfer_sent",amount=amount,account=sender,related_account=receiver,description=desc)
            Transaction.objects.create(transaction_type="transfer_received",amount=amount,account=receiver,related_account=sender,description=desc)
            return tx
