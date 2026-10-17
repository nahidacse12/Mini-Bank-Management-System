from django.contrib import admin
from .models import BankAccount,Transaction
@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display=("account_number","owner","account_type","balance","status","created_at")
    list_filter=("account_type","status"); search_fields=("account_number","owner__username","owner__email")
    readonly_fields=("account_number","created_at")
@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display=("reference","transaction_type","amount","account","related_account","created_at")
    list_filter=("transaction_type","created_at"); search_fields=("reference","account__account_number")
    readonly_fields=("reference","created_at")
