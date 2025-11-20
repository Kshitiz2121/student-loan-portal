"""
Payment Gateway Integration for Student Loan Portal

This module provides integration with popular Indian payment gateways
including Razorpay, PayU, and Paytm for processing loan repayments.
"""

import json
import requests
import hashlib
import hmac
import time
from decimal import Decimal
from django.conf import settings
from django.utils import timezone


class PaymentGatewayError(Exception):
    """Custom exception for payment gateway errors"""
    pass


class RazorpayGateway:
    """Razorpay payment gateway integration"""
    
    def __init__(self):
        self.key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        self.key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        self.base_url = 'https://api.razorpay.com/v1'
    
    def create_order(self, amount, currency='INR', receipt=None):
        """Create a Razorpay order"""
        if not self.key_id or not self.key_secret:
            raise PaymentGatewayError("Razorpay credentials not configured")
        
        url = f"{self.base_url}/orders"
        headers = {
            'Authorization': f'Basic {self._get_auth_string()}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'amount': int(amount * 100),  # Convert to paise
            'currency': currency,
            'receipt': receipt or f"loan_repayment_{int(time.time())}",
            'notes': {
                'payment_type': 'loan_repayment'
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Razorpay order creation failed: {str(e)}")
    
    def verify_payment(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """Verify Razorpay payment signature"""
        message = f"{razorpay_order_id}|{razorpay_payment_id}"
        generated_signature = hmac.new(
            self.key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(generated_signature, razorpay_signature)
    
    def capture_payment(self, payment_id, amount):
        """Capture authorized payment"""
        url = f"{self.base_url}/payments/{payment_id}/capture"
        headers = {
            'Authorization': f'Basic {self._get_auth_string()}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'amount': int(amount * 100)  # Convert to paise
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise PaymentGatewayError(f"Razorpay payment capture failed: {str(e)}")
    
    def _get_auth_string(self):
        """Get base64 encoded auth string"""
        import base64
        credentials = f"{self.key_id}:{self.key_secret}"
        return base64.b64encode(credentials.encode()).decode()


class PayUGateway:
    """PayU payment gateway integration"""
    
    def __init__(self):
        self.merchant_key = getattr(settings, 'PAYU_MERCHANT_KEY', '')
        self.salt = getattr(settings, 'PAYU_SALT', '')
        self.base_url = 'https://secure.payu.in/_payment'
    
    def create_payment_request(self, amount, firstname, email, phone, product_info, 
                              success_url, failure_url, service_provider='payu_paisa'):
        """Create PayU payment request"""
        if not self.merchant_key or not self.salt:
            raise PaymentGatewayError("PayU credentials not configured")
        
        txnid = f"TXN{int(time.time())}"
        
        # Create hash string for verification
        hash_string = f"{self.merchant_key}|{txnid}|{amount}|{product_info}|{firstname}|{email}|||||||||||{self.salt}"
        hash_value = hashlib.sha512(hash_string.encode()).hexdigest()
        
        return {
            'key': self.merchant_key,
            'txnid': txnid,
            'amount': str(amount),
            'productinfo': product_info,
            'firstname': firstname,
            'email': email,
            'phone': phone,
            'surl': success_url,
            'furl': failure_url,
            'hash': hash_value,
            'service_provider': service_provider
        }
    
    def verify_payment_response(self, response_data):
        """Verify PayU payment response"""
        # Extract required fields
        status = response_data.get('status')
        txnid = response_data.get('txnid')
        amount = response_data.get('amount')
        productinfo = response_data.get('productinfo')
        firstname = response_data.get('firstname')
        email = response_data.get('email')
        received_hash = response_data.get('hash')
        
        # Create hash string for verification
        hash_string = f"{self.salt}|{status}|||||||||||{email}|{firstname}|{productinfo}|{amount}|{txnid}|{self.merchant_key}"
        calculated_hash = hashlib.sha512(hash_string.encode()).hexdigest()
        
        return {
            'verified': hmac.compare_digest(calculated_hash, received_hash),
            'status': status,
            'txnid': txnid,
            'amount': amount
        }


class PaytmGateway:
    """Paytm payment gateway integration"""
    
    def __init__(self):
        self.merchant_id = getattr(settings, 'PAYTM_MERCHANT_ID', '')
        self.merchant_key = getattr(settings, 'PAYTM_MERCHANT_KEY', '')
        self.base_url = 'https://securegw-stage.paytm.in' if settings.DEBUG else 'https://securegw.paytm.in'
    
    def create_transaction(self, amount, order_id, customer_id, callback_url):
        """Create Paytm transaction"""
        if not self.merchant_id or not self.merchant_key:
            raise PaymentGatewayError("Paytm credentials not configured")
        
        # Create checksum
        paytm_params = {
            'MID': self.merchant_id,
            'ORDER_ID': order_id,
            'CUST_ID': customer_id,
            'TXN_AMOUNT': str(amount),
            'CHANNEL_ID': 'WEB',
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'DEFAULT',
            'CALLBACK_URL': callback_url,
            'MOBILE_NO': '',
            'EMAIL': ''
        }
        
        checksum = self._generate_checksum(paytm_params)
        paytm_params['CHECKSUMHASH'] = checksum
        
        return paytm_params
    
    def verify_transaction(self, response_data):
        """Verify Paytm transaction"""
        # Verify checksum
        received_checksum = response_data.get('CHECKSUMHASH')
        response_data.pop('CHECKSUMHASH', None)
        
        calculated_checksum = self._generate_checksum(response_data)
        
        return {
            'verified': hmac.compare_digest(calculated_checksum, received_checksum),
            'status': response_data.get('STATUS'),
            'txn_id': response_data.get('TXNID'),
            'amount': response_data.get('TXN_AMOUNT')
        }
    
    def _generate_checksum(self, params):
        """Generate Paytm checksum"""
        # This is a simplified version - in production, use the official Paytm SDK
        import base64
        import hmac
        import hashlib
        
        sorted_params = sorted(params.items())
        data_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        checksum = hmac.new(
            self.merchant_key.encode(),
            data_string.encode(),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(checksum).decode()


class PaymentGatewayManager:
    """Manager class for handling multiple payment gateways"""
    
    def __init__(self):
        self.razorpay = RazorpayGateway()
        self.payu = PayUGateway()
        self.paytm = PaytmGateway()
    
    def create_payment(self, gateway_name, amount, **kwargs):
        """Create payment using specified gateway"""
        if gateway_name.lower() == 'razorpay':
            return self.razorpay.create_order(amount, **kwargs)
        elif gateway_name.lower() == 'payu':
            return self.payu.create_payment_request(amount, **kwargs)
        elif gateway_name.lower() == 'paytm':
            return self.paytm.create_transaction(amount, **kwargs)
        else:
            raise PaymentGatewayError(f"Unsupported payment gateway: {gateway_name}")
    
    def verify_payment(self, gateway_name, **kwargs):
        """Verify payment using specified gateway"""
        if gateway_name.lower() == 'razorpay':
            return self.razorpay.verify_payment(**kwargs)
        elif gateway_name.lower() == 'payu':
            return self.payu.verify_payment_response(**kwargs)
        elif gateway_name.lower() == 'paytm':
            return self.paytm.verify_transaction(**kwargs)
        else:
            raise PaymentGatewayError(f"Unsupported payment gateway: {gateway_name}")


# Global payment gateway manager instance
payment_gateway = PaymentGatewayManager()


def process_payment(repayment, gateway_name='razorpay', **gateway_params):
    """
    Process payment for a repayment record
    
    Args:
        repayment: Repayment model instance
        gateway_name: Name of the payment gateway to use
        **gateway_params: Additional parameters for the gateway
    
    Returns:
        dict: Payment processing result
    """
    try:
        # Create payment using the specified gateway
        payment_data = payment_gateway.create_payment(
            gateway_name,
            float(repayment.amount_paid),
            **gateway_params
        )
        
        # Update repayment with gateway information
        repayment.gateway_transaction_id = payment_data.get('id') or payment_data.get('txnid')
        repayment.status = 'Processing'
        repayment.gateway_response = payment_data
        repayment.save()
        
        return {
            'success': True,
            'payment_data': payment_data,
            'gateway': gateway_name
        }
        
    except PaymentGatewayError as e:
        repayment.status = 'Failed'
        repayment.notes = f"Payment gateway error: {str(e)}"
        repayment.save()
        
        return {
            'success': False,
            'error': str(e),
            'gateway': gateway_name
        }
    except Exception as e:
        repayment.status = 'Failed'
        repayment.notes = f"Payment processing error: {str(e)}"
        repayment.save()
        
        return {
            'success': False,
            'error': str(e),
            'gateway': gateway_name
        }


def verify_payment(repayment, gateway_name='razorpay', **verification_params):
    """
    Verify payment for a repayment record
    
    Args:
        repayment: Repayment model instance
        gateway_name: Name of the payment gateway to use
        **verification_params: Parameters for payment verification
    
    Returns:
        dict: Payment verification result
    """
    try:
        # Verify payment using the specified gateway
        verification_result = payment_gateway.verify_payment(
            gateway_name,
            **verification_params
        )
        
        if verification_result.get('verified', False):
            repayment.status = 'Paid'
            current_response = repayment.gateway_response or {}
            current_response.update({'verification': verification_result})
            repayment.gateway_response = current_response
            repayment.save()
            
            return {
                'success': True,
                'verified': True,
                'status': verification_result.get('status'),
                'gateway': gateway_name
            }
        else:
            repayment.status = 'Failed'
            repayment.save()
            
            return {
                'success': False,
                'verified': False,
                'error': 'Payment verification failed',
                'gateway': gateway_name
            }
            
    except PaymentGatewayError as e:
        repayment.status = 'Failed'
        repayment.notes = f"Payment verification error: {str(e)}"
        repayment.save()
        
        return {
            'success': False,
            'error': str(e),
            'gateway': gateway_name
        }
    except Exception as e:
        repayment.status = 'Failed'
        repayment.notes = f"Payment verification error: {str(e)}"
        repayment.save()
        
        return {
            'success': False,
            'error': str(e),
            'gateway': gateway_name
        }
