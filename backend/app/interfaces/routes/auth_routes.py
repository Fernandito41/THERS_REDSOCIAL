from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.application.auth.login_use_case import login_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({"msg": "No se enviaron datos"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"msg": "Email y contraseña son obligatorios"}), 400

    user = login_user(email, password)

    if not user:
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    token = create_access_token(identity=user["email"])

    return jsonify({
        "token": token,
        "user": user
    }), 200