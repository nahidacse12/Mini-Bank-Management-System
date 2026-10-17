from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import ProfileView,BankAccountViewSet,DepositView,WithdrawalView,TransferView,TransactionListView,AdminCustomerListView,AdminAccountListView,AdminTransactionListView
router=DefaultRouter(); router.register("accounts",BankAccountViewSet,basename="account")
urlpatterns=[path("profile/",ProfileView.as_view()),path("transactions/deposit/",DepositView.as_view()),path("transactions/withdraw/",WithdrawalView.as_view()),path("transactions/transfer/",TransferView.as_view()),path("transactions/",TransactionListView.as_view()),path("admin/customers/",AdminCustomerListView.as_view()),path("admin/accounts/",AdminAccountListView.as_view()),path("admin/transactions/",AdminTransactionListView.as_view()),path("",include(router.urls))]
