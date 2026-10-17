from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BankAccount, Transaction
from .serializers import RegisterSerializer,ProfileSerializer,BankAccountSerializer,TransactionSerializer,DepositSerializer,WithdrawalSerializer,TransferSerializer
User=get_user_model()
class RegisterView(generics.CreateAPIView):
    queryset=User.objects.all(); serializer_class=RegisterSerializer; permission_classes=[AllowAny]
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer; permission_classes=[IsAuthenticated]
    def get_object(self): return self.request.user
class BankAccountViewSet(viewsets.ModelViewSet):
    serializer_class=BankAccountSerializer; permission_classes=[IsAuthenticated]
    http_method_names=["get","post","head","options"]
    def get_queryset(self):
        qs=BankAccount.objects.all() if self.request.user.is_staff else BankAccount.objects.filter(owner=self.request.user)
        return qs
    def perform_create(self,serializer): serializer.save(owner=self.request.user)
    @action(detail=True,methods=["get"],url_path="balance")
    def balance(self,request,pk=None):
        a=self.get_object()
        return Response({"account_number":a.account_number,"balance":a.balance,"currency":"EUR"})
class DepositView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        s=DepositSerializer(data=request.data,context={"request":request}); s.is_valid(raise_exception=True)
        return Response(TransactionSerializer(s.save()).data,status=status.HTTP_201_CREATED)
class WithdrawalView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        s=WithdrawalSerializer(data=request.data,context={"request":request}); s.is_valid(raise_exception=True)
        return Response(TransactionSerializer(s.save()).data,status=status.HTTP_201_CREATED)
class TransferView(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        s=TransferSerializer(data=request.data,context={"request":request}); s.is_valid(raise_exception=True)
        return Response(TransactionSerializer(s.save()).data,status=status.HTTP_201_CREATED)
class TransactionListView(generics.ListAPIView):
    serializer_class=TransactionSerializer; permission_classes=[IsAuthenticated]
    def get_queryset(self):
        qs=Transaction.objects.select_related("account","related_account").filter(account__owner=self.request.user)
        typ=self.request.query_params.get("type")
        if typ: qs=qs.filter(transaction_type=typ)
        return qs
class AdminCustomerListView(generics.ListAPIView):
    queryset=User.objects.all().order_by("id"); serializer_class=ProfileSerializer; permission_classes=[IsAdminUser]
class AdminAccountListView(generics.ListAPIView):
    queryset=BankAccount.objects.select_related("owner").all(); serializer_class=BankAccountSerializer; permission_classes=[IsAdminUser]
class AdminTransactionListView(generics.ListAPIView):
    queryset=Transaction.objects.select_related("account","related_account").all(); serializer_class=TransactionSerializer; permission_classes=[IsAdminUser]
