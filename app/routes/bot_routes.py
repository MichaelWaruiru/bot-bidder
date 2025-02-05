from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserModel
from app import mysql

bot_bp = Blueprint("bot", __name__)
user_model = UserModel(mysql)

@bot_bp.route("/")
def bot_dashboard():
  return render_template("bot_dashboard.html")

@bot_bp.route("/activate", methods=["POST"])
@jwt_required()
def activate_bot():
    user = get_jwt_identity()
    user_data = user_model.get_user_by_email(user[2])
    
    if user_data and user_data[5]:  # subscription_active
        user_model.update_bot_status(user_data[0], True)
        return jsonify({"msg": "Bot activated successfully"}), 200
    return jsonify({"msg": "Subscription not active"}), 403

@bot_bp.route("/status", methods=["GET"])
@jwt_required()
def bot_status():
    user = get_jwt_identity()
    user_data = user_model.get_user_by_email(user[2])

    if user_data:
        return jsonify({"bot_active": bool(user_data[6])}), 200
    return jsonify({"msg": "User not found"}), 404
