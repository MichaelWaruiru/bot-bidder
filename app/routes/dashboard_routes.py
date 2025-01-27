from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.utils.mpesa import initiate_payment
import os

dashboard_bp = Blueprint("dashboard_bp", __name__)

# Load subscription amount
SUBSCRIPTION_AMOUNT = os.getenv("SUBSCRIPTION_AMOUNT")


@dashboard_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
  user = get_jwt_identity() # Get logged-in user details from JWT
  access_token = session.get("access_token")
  return render_template("dashboard.html", username=user["email"], access_token=access_token)

@dashboard_bp.route("/get-subscription-price", methods=["GET"])
def get_subscription_price():
  """Fetch the static subscription price"""
  return jsonify({"amount": SUBSCRIPTION_AMOUNT}), 200

@dashboard_bp.route("/pay", methods=["POST"])
@jwt_required()
def pay():
  """Handle payment request via MPesa STK push"""
  user = get_jwt_identity()
  phone_number = user.get("phone_number") # Retrieve number from session or database
  if not phone_number:
    flash("Phone number not found!", "danger")
    return redirect(url_for("dashboard_bp.dashboard"))
  
  try:
    response = initiate_payment(phone_number, SUBSCRIPTION_AMOUNT)
    if response.get("ResponseCode") == "0":
      flash("Payment request sent successfully. Please check your phone.", "success")
    else:
      flash("Payment request failed. Try again later.", "danger")
  except Exception as e:
    flash(f"Error proccessing payment: {str(e)}", "danger")
    
  return redirect(url_for("dashboard_bp.dashboard"))