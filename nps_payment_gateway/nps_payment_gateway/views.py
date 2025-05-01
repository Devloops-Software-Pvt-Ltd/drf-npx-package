import hmac
import hashlib
import base64
import requests
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
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
    ProcessIdResponseSerializer,
    TransactionStatusResponseSerializer
)



class NpsPaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing NPS Payment configurations"""
    
    queryset = NpsPayment.objects.all()
    serializer_class = NpsPaymentSerializer
    http_method_names = ['get', 'post', 'put', 'patch']

    def list(self, request):
        payments = NpsPayment.objects.all()
        serializer = NpsPaymentSerializer(payments, many=True)
        return Response({"data": serializer.data})

    def create(self, request, *args, **kwargs):
        # Check if NPS payment configuration already exists
        if NpsPayment.objects.exists():
            return Response({
                "code": "1",
                "message": "Error",
                "errors": [{
                    "error_code": "400",
                    "error_message": "NPS payment configuration already exists. Only one record is allowed."
                }]
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "code": "0",
                "message": "Success",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            "code": "1",
            "message": "Error",
            "errors": [{
                "error_code": "400",
                "error_message": serializer.errors
            }]
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "code": "0",
                "message": "Success",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
            
        return Response({
            "code": "1",
            "message": "Error",
            "errors": [{
                "error_code": "400",
                "error_message": serializer.errors
            }]
        }, status=status.HTTP_400_BAD_REQUEST)

class NPSBaseAPIView(APIView):
    """Base class for NPS API operations"""
    
    def get_nps_config(self):
        """Get NPS payment configuration"""
        try:
            nps_config = NpsPayment.objects.first()
            if not nps_config:
                raise ValueError("NPS payment configuration not found")
            return nps_config
        except Exception as e:
            raise ValueError(f"Error getting NPS configuration: {str(e)}")

    def generate_hmac_sha512(self, message, secret_key):
        """Generate HMAC SHA512 signature"""
        try:
            # Convert message and secret key to bytes
            message_bytes = message.encode('utf-8')
            key_bytes = secret_key.encode('utf-8')
            
            # Create HMAC object
            hmac_obj = hmac.new(key_bytes, message_bytes, hashlib.sha512)
            
            # Generate signature and convert to lowercase hex string
            signature = hmac_obj.hexdigest().lower()
            
            return signature
        except Exception as e:
            raise ValueError(f"Error generating signature: {str(e)}")

    def get_headers(self, nps_config):
        """Get headers for API request"""
        try:
            # Create basic auth string
            auth_string = f"{nps_config.api_username}:{nps_config.api_password}"
            auth_bytes = auth_string.encode('utf-8')
            auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
            
            return {
                'Authorization': f'Basic {auth_base64}',
                'Content-Type': 'application/json'
            }
        except Exception as e:
            raise ValueError(f"Error generating headers: {str(e)}")

    def get_error_response(self, error_message, error_code="400", status_code=status.HTTP_400_BAD_REQUEST):
        """Generate standardized error response"""
        # Convert serializer errors to a more readable format
        if isinstance(error_message, dict):
            formatted_errors = []
            for field, errors in error_message.items():
                if isinstance(errors, list):
                    for error in errors:
                        # Get just the error message from ErrorDetail
                        error_str = error if isinstance(error, str) else error.message
                        formatted_errors.append({
                            "error_code": error_code,
                            "error_message": error_str
                        })
                else:
                    # Get just the error message from ErrorDetail
                    error_str = errors if isinstance(errors, str) else errors.message
                    formatted_errors.append({
                        "error_code": error_code,
                        "error_message": error_str
                    })
            return Response({
                "code": "1",
                "message": "Error",
                "errors": formatted_errors
            }, status=status_code)
        
        return Response({
            "code": "1",
            "message": "Error",
            "errors": [
                {
                    "error_code": error_code,
                    "error_message": str(error_message)
                }
            ]
        }, status=status_code)

    def make_api_request(self, url, payload, headers):
        """Make API request with error handling"""
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            # Log the request and response for debugging
            print(f"Request URL: {url}")
            print(f"Request Payload: {payload}")
            print(f"Response Status: {response.status_code}")
            print(f"Response Content: {response.text}")
            
            # Check for HTTP errors
            if response.status_code >= 400:
                error_message = f"HTTP {response.status_code}: {response.text}"
                return {
                    "code": "1",
                    "message": "Error",
                    "errors": [{
                        "error_code": str(response.status_code),
                        "error_message": error_message
                    }]
                }
            
            # Parse JSON response
            try:
                return response.json()
            except ValueError:
                return {
                    "code": "1",
                    "message": "Error",
                    "errors": [{
                        "error_code": "500",
                        "error_message": "Invalid JSON response from server"
                    }]
                }
                
        except requests.RequestException as e:
            return {
                "code": "1",
                "message": "Error",
                "errors": [{
                    "error_code": "500",
                    "error_message": f"Request failed: {str(e)}"
                }]
            }
        except Exception as e:
            return {
                "code": "1",
                "message": "Error",
                "errors": [{
                    "error_code": "500",
                    "error_message": f"Unexpected error: {str(e)}"
                }]
            }

    def handle_response(self, response_data, response_serializer_class):
        """
        Handle NPS API response with proper code handling
        code "0": Success
        code "1": Error
        code "2": Pending/In Process
        """
        try:
            if not isinstance(response_data, dict):
                return self.get_error_response("Invalid response format")

            response_code = response_data.get('code')
            
            if response_code == "0":
                # Success case
                response_serializer = response_serializer_class(data=response_data)
                if response_serializer.is_valid():
                    return Response(response_serializer.data, status=status.HTTP_200_OK)
                return self.get_error_response(response_serializer.errors)
                
            elif response_code == "1":
                # Error case
                return Response({
                    "code": "1",
                    "message": "Error",
                    "errors": response_data.get('errors', [
                        {
                            "error_code": "400",
                            "error_message": response_data.get('message', 'Unknown error occurred')
                        }
                    ])
                }, status=status.HTTP_400_BAD_REQUEST)
                
            elif response_code == "2":
                # Pending/In Process case
                return Response({
                    "code": "2",
                    "message": response_data.get('message', 'Transaction in process'),
                    "data": response_data.get('data', {})
                }, status=status.HTTP_202_ACCEPTED)
                
            else:
                # Unexpected code
                return self.get_error_response(
                    f"Unexpected response code: {response_code}",
                    error_code="500",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            return self.get_error_response(
                str(e),
                error_code="500",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PaymentInstrumentView(NPSBaseAPIView):
    """API view for getting payment instruments"""
    
    def post(self, request):
        try:
            serializer = PaymentInstrumentRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            nps_config = self.get_nps_config()
            
            payload = {
                "MerchantId": nps_config.merchant_id,
                "MerchantName": nps_config.merchant_name,
            }

            signature_string = f"{payload['MerchantId']}{payload['MerchantName']}"
            payload["Signature"] = self.generate_hmac_sha512(
                signature_string, 
                nps_config.gateway_api_secret_key
            )

            response_data = self.make_api_request(
                'https://apisandbox.nepalpayment.com/GetPaymentInstrumentDetails',
                payload,
                self.get_headers(nps_config)
            )
            
            return self.handle_response(response_data, PaymentInstrumentResponseSerializer)

        except serializer.ValidationError as e:
            return self.get_error_response(e.detail)
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            return self.get_error_response(str(e), "500", status.HTTP_500_INTERNAL_SERVER_ERROR)

class ServiceChargeView(NPSBaseAPIView):
    """API view for getting service charges"""
    
    def post(self, request):
        try:
            serializer = ServiceChargeRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            nps_config = self.get_nps_config()
            
            payload = {
                "MerchantId": nps_config.merchant_id,
                "MerchantName": nps_config.merchant_name,
                "Amount": str(serializer.validated_data['amount']),
                "InstrumentCode": serializer.validated_data['payment_instrument_id']
            }

            signature_string = (
                f"{payload['Amount']}{payload['MerchantId']}"
                f"{payload['MerchantName']}{payload['InstrumentCode']}"
            )
            payload["Signature"] = self.generate_hmac_sha512(
                signature_string, 
                nps_config.gateway_api_secret_key
            )

            response_data = self.make_api_request(
                'https://apisandbox.nepalpayment.com/GetServiceCharge',
                payload,
                self.get_headers(nps_config)
            )
            
            return self.handle_response(response_data, ServiceChargeResponseSerializer)

        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            return self.get_error_response(str(e), "500", status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProcessIdView(NPSBaseAPIView):
    """API view for getting process ID"""
    
    def post(self, request):
        try:
            serializer = ProcessIdRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return self.get_error_response(serializer.errors)

            nps_config = self.get_nps_config()
            
            payload = {
                "MerchantId": nps_config.merchant_id,
                "MerchantName": nps_config.merchant_name,
                "Amount": str(serializer.validated_data['amount']),
                "MerchantTxnId": serializer.validated_data['merchant_txn_id']
            }

            signature_string = (
                f"{payload['Amount']}{payload['MerchantId']}"
                f"{payload['MerchantName']}{payload['MerchantTxnId']}"
            )
            payload["Signature"] = self.generate_hmac_sha512(
                signature_string, 
                nps_config.gateway_api_secret_key
            )

            response_data = self.make_api_request(
                'https://apisandbox.nepalpayment.com/GetProcessId',
                payload,
                self.get_headers(nps_config)
            )
            
            return self.handle_response(response_data, ProcessIdResponseSerializer)

        except serializer.ValidationError as e:
            return self.get_error_response(e.detail)
        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            return self.get_error_response(str(e), "500", status.HTTP_500_INTERNAL_SERVER_ERROR)

class NotificationView(NPSBaseAPIView):
    """API view for handling NPS notifications"""
    
    def get(self, request):
        try:
            serializer = NotificationRequestSerializer(data=request.query_params)
            serializer.is_valid(raise_exception=True)

            nps_config = self.get_nps_config()
            
            payload = {
                "MerchantId": nps_config.merchant_id,
                "MerchantName": nps_config.merchant_name,
                "MerchantTxnId": serializer.validated_data['merchant_txn_id']
            }

            signature_string = (
                f"{payload['MerchantId']}{payload['MerchantName']}"
                f"{payload['MerchantTxnId']}"
            )
            payload["Signature"] = self.generate_hmac_sha512(
                signature_string, 
                nps_config.gateway_api_secret_key
            )

            response_data = self.make_api_request(
                'https://apisandbox.nepalpayment.com/CheckTransactionStatus',
                payload,
                self.get_headers(nps_config)
            )

            # Handle transaction status response
            status_response = self.handle_response(response_data, TransactionStatusResponseSerializer)
            
            # If transaction is successful (code "0"), return "received"
            if response_data.get('code') == "0":
                return Response(
                    "received",
                    content_type="text/plain",
                    status=status.HTTP_200_OK
                )
            
            # For pending transactions (code "2"), return "in process"
            if response_data.get('code') == "2":
                return Response(
                    "in process",
                    content_type="text/plain",
                    status=status.HTTP_202_ACCEPTED
                )
            
            # For failed transactions (code "1"), return error response
            return status_response

        except ValueError as e:
            return self.get_error_response(str(e))
        except Exception as e:
            return self.get_error_response(str(e), "500", status.HTTP_500_INTERNAL_SERVER_ERROR)





