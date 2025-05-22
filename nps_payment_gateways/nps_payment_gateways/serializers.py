from rest_framework import serializers
from .models import NpsPayment

# Base Error Serializer
class ErrorDetailSerializer(serializers.Serializer):
    error_code = serializers.CharField()
    error_message = serializers.CharField()

# Base Response Serializer
class BaseResponseSerializer(serializers.Serializer):
    code = serializers.ChoiceField(choices=['0', '1', '2'])
    message = serializers.CharField()
    errors = ErrorDetailSerializer(many=True, required=False)

    def validate(self, data):
        """
        Check that either errors or data is present based on code
        """
        code = data.get('code')
        errors = data.get('errors', [])
        
        if code == '1' and not errors:
            raise serializers.ValidationError("Errors must be present when code is '1'")
        
        return data

# Payment Instrument Serializers
class PaymentInstrumentRequestSerializer(serializers.Serializer):
    merchant_id = serializers.CharField(required=False)
    merchant_name = serializers.CharField(required=False)

class PaymentInstrumentDataSerializer(serializers.Serializer):
    InstitutionName = serializers.CharField()
    InstrumentName = serializers.CharField()
    InstrumentCode = serializers.CharField()
    InstrumentValue = serializers.CharField(allow_null=True, required=False)
    LogoUrl = serializers.URLField()
    BankUrl = serializers.CharField()
    BankType = serializers.CharField()

class PaymentInstrumentResponseSerializer(BaseResponseSerializer):
    data = PaymentInstrumentDataSerializer(many=True, required=False)

    def validate(self, data):
        return data

# Service Charge Serializers
class ServiceChargeRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=0.01
    )
    payment_instrument_id = serializers.CharField()

class ServiceChargeDataSerializer(serializers.Serializer):
    Amount = serializers.CharField()
    CommissionType = serializers.CharField()
    ChargeValue = serializers.CharField()
    TotalChargeAmount = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2,
        min_value=0
    )

class ServiceChargeResponseSerializer(BaseResponseSerializer):
    data = ServiceChargeDataSerializer(required=False)

    def validate(self, data):
        return data

# Process ID Serializers
class ProcessIdRequestSerializer(serializers.Serializer):
    amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2,
        min_value=0.01,
        error_messages={
            'required': 'Amount is required for payment processing'
        }
    )
    merchant_txn_id = serializers.CharField(
        max_length=50,
        error_messages={
            'required': 'Merchant Transaction ID is required'
        }
    )
    TransactionRemarks = serializers.CharField(
        max_length=255,
        error_messages={
            'required': 'TransactionRemarks is required'
        }
    )
    InstrumentCode = serializers.CharField(
        max_length=255,
        error_messages={
            'required': 'TransactionRemarks is required'
        }
    )

    def validate_merchant_txn_id(self, value):
        """
        Validate merchant transaction ID format
        """
        if len(value) < 5:
            raise serializers.ValidationError(
                "Merchant transaction ID must be at least 5 characters long"
            )
        return value

class ProcessIdDataSerializer(serializers.Serializer):
    ProcessId = serializers.CharField()

class ProcessIdResponseSerializer(BaseResponseSerializer):
    data = ProcessIdDataSerializer(required=False)

    def validate(self, data):
        return data

# Transaction Status Serializers
class TransactionStatusRequestSerializer(serializers.Serializer):
    merchant_txn_id = serializers.CharField()

class TransactionStatusDataSerializer(serializers.Serializer):
    GatewayReferenceNo = serializers.CharField()
    Amount = serializers.CharField()
    ServiceCharge = serializers.CharField()
    TransactionRemarks = serializers.CharField(allow_blank=True)
    TransactionRemarks2 = serializers.CharField(allow_blank=True, required=False)
    TransactionRemarks3 = serializers.CharField(allow_blank=True, required=False)
    ProcessId = serializers.CharField()
    TransactionDate = serializers.CharField()
    MerchantTxnId = serializers.CharField()
    CbsMessage = serializers.CharField(allow_blank=True)
    Status = serializers.ChoiceField(choices=['Success', 'Fail', 'Pending'])
    Institution = serializers.CharField()
    Instrument = serializers.CharField()
    PaymentCurrency = serializers.CharField(required=False, default='NPR')
    ExchangeRate = serializers.CharField(required=False, default='1')

class TransactionStatusResponseSerializer(BaseResponseSerializer):
    data = TransactionStatusDataSerializer(required=False)

    def validate(self, data):
        return data

# Notification Serializers
class NotificationRequestSerializer(serializers.Serializer):
    merchant_txn_id = serializers.CharField(required=True, allow_blank=False)
    gateway_txn_id = serializers.CharField(required=True, allow_blank=False)

# NPS Payment Configuration Serializer
class NpsPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NpsPayment
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def validate_merchant_id(self, value):
        """
        Validate merchant ID format
        """
        if not value.strip():
            raise serializers.ValidationError("Merchant ID cannot be empty")
        return value

    def validate_merchant_name(self, value):
        """
        Validate merchant name format
        """
        if not value.strip():
            raise serializers.ValidationError("Merchant name cannot be empty")
        return value




class NPSErrorSerializer(serializers.Serializer):
    error_code = serializers.CharField()
    error_message = serializers.CharField()





