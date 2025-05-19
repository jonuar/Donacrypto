from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.security import generate_password_hash
import secrets

from ..models.user import User
from ..models.password_reset import PasswordResetToken
from ..decorators.role_required import role_required
from ..extensions import mongo
from ..extensions import blacklist

auth_bp = Blueprint("auth_bp", __name__)

# Límites de longitud
MAX_USERNAME_LENGTH = 30
MAX_EMAIL_LENGTH = 100
MAX_PASSWORD_LENGTH = 128

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = request.get_json()

        # Validar datos
        if not data or not all(k in data for k in ("username", "email", "password", "role")):
            return jsonify({"error": "Faltan datos"}), 400

        # Validar longitudes
        if len(data["username"]) > MAX_USERNAME_LENGTH:
            return jsonify({"error": "Username demasiado largo"}), 400
        if len(data["email"]) > MAX_EMAIL_LENGTH:
            return jsonify({"error": "Email demasiado largo"}), 400
        if len(data["password"]) > MAX_PASSWORD_LENGTH:
            return jsonify({"error": "Contraseña demasiado larga"}), 400

        # Validar email
        if User.find_by_email(data["email"]):
            return jsonify({"error": "El usuario ya existe"}), 409

        user = User(data["username"], data["email"], data["password"], data["role"])
        if user.save_to_db():
            return jsonify({"message": "Usuario registrado con éxito"}), 201
        else:
            return jsonify({"error": "Error al registrar usuario"}), 500

    except Exception as e:
        current_app.logger.error(f"[register] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        # Validar datos
        if not data or not all(k in data for k in ("email", "password")):
            return jsonify({"error": "Faltan datos"}), 400

        # Validar longitudes
        if len(data["email"]) > MAX_EMAIL_LENGTH or len(data["password"]) > MAX_PASSWORD_LENGTH:
            return jsonify({"error": "Datos demasiado largos"}), 400

        # Autenticar user
        user = User.find_by_email(data["email"])
        if user and user.check_password(data["password"]):
            token = user.generate_token()
            return jsonify({"access_token": token}), 200
        else:
            return jsonify({"error": "Credenciales incorrectas"}), 401

    except Exception as e:
        current_app.logger.error("[login] Error: {}".format(e))
        return jsonify({"error": "Error interno del servidor"}), 500
    

@auth_bp.route("/request-reset", methods=["POST"])
def request_password_reset():
    """Solicita el envío de un token para restablecer contraseña"""

    data = request.get_json()
    email = data.get("email")

    # Verifica el email enviado y el usuario en la base de datos
    if not email or not User.find_by_email(email):
        return jsonify({"error": "Email no registrado"}), 404

    # Genera un token único y seguro para el restablecimiento de contraseña
    token = secrets.token_urlsafe(32)
    
    # Guarda el token en la base de datos con una fecha de expiración
    if PasswordResetToken.save_token(email, token):
        # El token puede ser enviado por correo, o simplemente devolverlo si es para frontend
        return jsonify({"message": "Token generado", "reset_token": token}), 200
    else:
        return jsonify({"error": "Error generando token"}), 500


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Cambia la contraseña si el token es válido"""

    data = request.get_json()
    token = data.get("token")
    new_password = data.get("new_password")

    # Verifica que ambos campos (token y nueva contraseña) estén presentes
    if not token or not new_password:
        return jsonify({"error": "Datos incompletos"}), 400

    # Verifica si el token es válido y no ha expirado
    email = PasswordResetToken.verify_token(token)
    if not email:
        return jsonify({"error": "Token inválido o expirado"}), 400

    # Si el token es válido, cambia la contraseña
    try:
        # Cifra la nueva contraseña
        hashed_password = generate_password_hash(new_password)
        # Actualiza la contraseña del usuario en la base de datos
        mongo.db.users.update_one({"email": email}, {"$set": {"password": hashed_password}})
        # Elimina el token después de usarlo para evitar su reutilización
        PasswordResetToken.delete_token(token)
        
        return jsonify({"message": "Contraseña actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error actualizando contraseña"}), 500 

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_profile():
    """"Devuelve perfil del usuario logueado"""
    try:
        email = get_jwt_identity()
        user = User.find_by_email(email)
        if user:
            return jsonify({
                "username": user.username,
                "email": user.email,
                "role": user.role
            }), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404
    except Exception as e:
        current_app.logger.error(f"[get_profile] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """Invalida el token actual (agrega a la lista negra)"""
    try:
        jti = get_jwt()["jti"]  # JWT ID
        blacklist.add(jti)
        return jsonify({"message": "Sesión cerrada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al cerrar sesión"}), 500

@auth_bp.route("/feed", methods=["GET"])
@jwt_required()
def user_feed():
    try:
        current_user = get_jwt_identity()
        user_data = mongo.db.users.find_one({"email": current_user}, {"_id": 0, "username": 1})
        if not user_data:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify({"message": f"Bienvenido, {current_user}"}), 200
    except Exception as e:
        current_app.logger.error(f"[protected] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    
@auth_bp.route("/creators", methods=["GET"])
@jwt_required()
def get_creators():
    """Directorio de creadores"""
    try:
        creators_data = mongo.db.users.find({"role": "creator"}, {"_id": 0, "username": 1, "email": 1})
        creators = list(creators_data)
        if not creators:
            return jsonify({"message": "No hay creadores disponibles."}), 404
        return jsonify(creators), 200
    except Exception as e:
        current_app.logger.error(f"[get_all_creators] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

# Para los Followers es necesario dashboard? Ver referencias (Buy Me a Coffee, Cafecito, KoFi)