import os
import requests
import base64
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MPESA_ENV = os.getenv('MPESA_ENV', 'sandbox')
BASE_URL = "https://sandbox.safaricom.co.ke" if MPESA_ENV == "sandbox" else "https://api.safaricom.co.ke"

CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
SHORTCODE = os.getenv("MPESA_SHORTCODE")
PASSKEY = os.getenv("MPESA_PASSKEY")
CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")

def get_access_token():
    """Retrieve MPesa access token."""
    auth_url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(auth_url, auth=(CONSUMER_KEY, CONSUMER_SECRET))
    response_data = response.json()
    return response_data['access_token']

def initiate_payment(phone_number, amount):
    """Initiate MPesa STK push request."""
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((SHORTCODE + PASSKEY + timestamp).encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "SubscriptionPayment",
        "TransactionDesc": "Payment for monthly bot subscription"
    }

    stk_url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
    response = requests.post(stk_url, json=payload, headers=headers)
    return response.json()
