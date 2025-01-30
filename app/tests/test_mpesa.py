import os
import json
from dotenv import load_dotenv
from mpesa import get_access_token, initiate_payment
from datetime import datetime
import base64
import re

# Load environment variables from .env file
load_dotenv()

def validate_phone_number(phone_number):
  """Validates phone number format (must start with +254 for Kenya or similar country code)."""
  phone_number = phone_number.strip()  # Remove any trailing spaces
  if phone_number.startswith('+'):
      phone_number = phone_number[1:]  # Remove the '+' symbol
  pattern = r"^\d{12}$"  # Ensure it's 12 digits long (without the '+' sign)
  return bool(re.match(pattern, phone_number))

def get_dynamic_phone_number():
    """Retrieve and clean dynamic phone number input."""
    phone_number = input("Enter Phone Number (e.g. +254719453367): ").strip()
    # Clean the phone number (remove non-numeric characters if needed)
    if phone_number.startswith('+'):
        phone_number = phone_number[1:]  # Remove the '+' symbol
    return phone_number
  

def test_access_token():
  """Test token generation"""
  try:
      # Try to get the access token
      access_token = get_access_token()
      print(f"Access Token: {access_token}")
      return access_token
  except Exception as e:
      print(f"Error while getting access token: {e}")
      return None

def test_payment_initiation(amount):
    """Test payment initiation"""
    try:
        phone_number = get_dynamic_phone_number()

        # Validate phone number format
        if not validate_phone_number(phone_number):
            print(f"Invalid phone number format: {phone_number}. Please use the international format.")
            return

        # Get the access token
        access_token = test_access_token()
        if not access_token:
            print("Skipping payment initiation due to missing token.")
            return

        # Prepare the timestamp and password as done in the actual function
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((str(os.getenv("MPESA_SHORTCODE")) + os.getenv("MPESA_PASSKEY") + timestamp).encode()).decode()

        # Prepare headers and payload
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "BusinessShortCode": os.getenv("MPESA_SHORTCODE"),
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,  # Dynamically passed phone number
            "PartyB": os.getenv("MPESA_SHORTCODE"),
            "PhoneNumber": phone_number,  # Dynamically passed phone number
            "CallBackURL": os.getenv("MPESA_CALLBACK_URL"),
            "AccountReference": "SubscriptionPayment",
            "TransactionDesc": "Payment for monthly bot subscription"
        }

        # Log the payload for debugging
        print(f"Payload: {json.dumps(payload, indent=4)}")

        # Make the payment initiation request
        response = initiate_payment(phone_number, amount)
        
        # Print the response
        print(f"Payment Initiation Response: {json.dumps(response, indent=4)}")
        
        if response.get("ResponseCode") == "0":
            print(f"Payment request successful. CheckoutRequestID: {response.get('CheckoutRequestID')}")
        else:
            print(f"Payment request failed with error: {json.dumps(response, indent=4)}")
    
    except Exception as e:
        print(f"Error during payment initiation: {e}")


if __name__ == "__main__":
    # Example phone number and subscription amount for testing
    # test_phone_number = "+254719453367"  # Replace with an actual test phone number in international format
    test_amount = 5  # You can adjust the test amount
    
    test_payment_initiation(test_amount)
