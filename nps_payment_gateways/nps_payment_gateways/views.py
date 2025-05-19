import hmac
import hashlib
import base64
import requests
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from .models import NpsPayment
from .serializers import (
    NpsPaymentSerializer,
    PaymentInstrumentRequestSerializer,
    ProcessIdRequestSerializer,
    NotificationRequestSerializer,
    ServiceChargeRequestSerializer,
    PaymentInstrumentResponseSerializer,
    ServiceChargeResponseSerializer,
)
from rest_framework import serializers

class NpsPaymentViewSet(viewsets.ModelViewSet):
    queryset = NpsPayment.objects.all()
    serializer_class = NpsPaymentSerializer
    http_method_names = ['get', 'post', 'put', 'patch']

    def list(self, request):
        payments = self.queryset
        serializer = self.serializer_class(payments, many=True)
        return Response({"code": "0", "message": "Payment configurations retrieved successfully.", "data": serializer.data})

    def create(self, request, *args, **kwargs):
        if self.queryset.exists():
            return Response({
                "code": "1",
                "message": "Only one configuration is allowed. Please update the existing one.",
                "error_code": "400"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({"code": "0", "message": "Configuration saved successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)

        return Response({"code": "1", "message": "Invalid input.", "error_code": "400", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({"code": "0", "message": "Configuration updated successfully.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response({"code": "1", "message": "Update failed due to invalid input.", "error_code": "400", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class NPSBaseAPIView(APIView):
    def get_nps_config(self):
        try:
            nps_config = NpsPayment.objects.first()
            if not nps_config:
                raise ValueError("NPS configuration is missing.")
            return nps_config
        except Exception as e:
            raise ValueError("Unable to load configuration. Please try again later.")

    def generate_hmac_sha512(self, message, secret_key):
        try:
            return hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha512).hexdigest().lower()
        except Exception:
            raise ValueError("Failed to generate signature.")

    def get_headers(self, config):
        try:
            auth = f"{config.api_username}:{config.api_password}"
            return {
                'Authorization': f'Basic {base64.b64encode(auth.encode()).decode()}',
                'Content-Type': 'application/json'
            }
        except Exception:
            raise ValueError("Failed to create request headers.")

    def get_error_response(self, message, error_code="400", status_code=status.HTTP_400_BAD_REQUEST):
        return Response({"code": "1", "message": message, "error_code": error_code}, status=status_code)

    def make_api_request(self, url, payload, headers):
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError:
            return {"code": "1", "message": "Gateway returned an error.", "error_code": "400"}
        except ValueError:
            return {"code": "1", "message": "Received an unexpected response from the server.", "error_code": "500"}
        except Exception:
            return {"code": "1", "message": "Unable to connect to the payment server.", "error_code": "500"}

    def handle_response(self, response_data, serializer_class):
        if response_data.get('code') == '0':
            serializer = serializer_class(data=response_data)
            if serializer.is_valid():
                return Response({"code": "0", "message": "Success.", "data": serializer.data}, status=status.HTTP_200_OK)
            return self.get_error_response("Invalid data format received from payment server.")
        elif response_data.get('code') == '2':
            return Response({"code": "2", "message": "Processing.", "data": response_data.get("data", {})}, status=status.HTTP_202_ACCEPTED)
        return self.get_error_response(response_data.get("message", "Unknown error occurred."))

class PaymentInstrumentView(NPSBaseAPIView):
    def post(self, request):
        try:
            serializer = PaymentInstrumentRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            config = self.get_nps_config()
            payload = {
                "MerchantId": config.merchant_id,
                "MerchantName": config.merchant_name
            }
            payload["Signature"] = self.generate_hmac_sha512(payload["MerchantId"] + payload["MerchantName"], config.gateway_api_secret_key)
            response_data = self.make_api_request("https://apisandbox.nepalpayment.com/GetPaymentInstrumentDetails", payload, self.get_headers(config))
            return self.handle_response(response_data, PaymentInstrumentResponseSerializer)
        except serializers.ValidationError as e:
            return self.get_error_response("Invalid request input.")
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception:
            return self.get_error_response("An unexpected error occurred.", error_code="500", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceChargeView(NPSBaseAPIView):
    def post(self, request):
        try:
            serializer = ServiceChargeRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            config = self.get_nps_config()
            payload = {
                "MerchantId": config.merchant_id,
                "MerchantName": config.merchant_name,
                "Amount": str(serializer.validated_data['amount']),
                "InstrumentCode": serializer.validated_data['payment_instrument_id']
            }
            signature_str = f"{payload['Amount']}{payload['MerchantId']}{payload['MerchantName']}{payload['InstrumentCode']}"
            payload["Signature"] = self.generate_hmac_sha512(signature_str, config.gateway_api_secret_key)
            response_data = self.make_api_request("https://apisandbox.nepalpayment.com/GetServiceCharge", payload, self.get_headers(config))
            return self.handle_response(response_data, ServiceChargeResponseSerializer)
        except Exception as e:
            return self.get_error_response(str(e), "500")

class ProcessIdView(NPSBaseAPIView):
    def post(self, request):
        try:
            serializer = ProcessIdRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            config = self.get_nps_config()
            payload = {
                "MerchantId": config.merchant_id,
                "MerchantName": config.merchant_name,
                "Amount": str(serializer.validated_data['amount']),
                "MerchantTxnId": serializer.validated_data['merchant_txn_id']
            }
            signature_str = f"{payload['Amount']}{payload['MerchantId']}{payload['MerchantName']}{payload['MerchantTxnId']}"
            payload["Signature"] = self.generate_hmac_sha512(signature_str, config.gateway_api_secret_key)
            response_data = self.make_api_request("https://apisandbox.nepalpayment.com/GetProcessId", payload, self.get_headers(config))
            if response_data.get('code') == '0':
                return Response({"code": "0", "message": "Process ID fetched successfully.", "data": response_data.get('data', {})}, status=status.HTTP_200_OK)
            return self.get_error_response(response_data.get("message", "Could not retrieve process ID."))
        except Exception:
            return self.get_error_response("Failed to get process ID.", "500")

class NotificationView(NPSBaseAPIView):
    def post(self, request):
        try:
            serializer = NotificationRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            merchant_txn_id = serializer.validated_data['merchant_txn_id']
            config = self.get_nps_config()
            payload = {
                "MerchantId": config.merchant_id,
                "MerchantName": config.merchant_name,
                "MerchantTxnId": merchant_txn_id
            }
            payload["Signature"] = self.generate_hmac_sha512(f"{payload['MerchantId']}{payload['MerchantName']}{payload['MerchantTxnId']}", config.gateway_api_secret_key)
            response_data = self.make_api_request("https://apisandbox.nepalpayment.com/CheckTransactionStatus", payload, self.get_headers(config))
            txn_data = response_data.get("data")
            if not txn_data:
                raise ValueError("No transaction information returned.")
            status_str = txn_data.get("Status", "").lower()
            if status_str == "success":
                return Response({"code": "0", "message": "Payment successful.", "data": txn_data}, status=200)
            elif status_str == "pending":
                return Response({"code": "2", "message": "Payment is pending.", "data": txn_data}, status=200)
            return Response({"code": "1", "message": f"Payment failed. Reason: {txn_data.get('CbsMessage', 'Unknown error')}", "data": txn_data}, status=400)
        except Exception as e:
            return self.get_error_response("Could not process payment notification.", error_code="500", status_code=500)