from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt, create_access_token
from werkzeug.security import generate_password_hash
import secrets
from datetime import timedelta
from typing import Dict, Any, Optional, Tuple

from ..models.user import User
from ..models.password_reset import PasswordResetToken
from ..extensions import mongo
from ..extensions import blacklist

auth_bp = Blueprint("auth_bp", __name__)

# Límites de longitud
MIN_USERNAME_LENGTH: int = 5
MAX_USERNAME_LENGTH: int = 30
MAX_EMAIL_LENGTH: int = 100
MAX_PASSWORD_LENGTH: int = 128


# FUNCIONES AUXILIARES


def find_by_email(email: str) -> Optional[Dict[str, Any]]:
    """
    Busca un usuario por su correo electrónico en la base de datos
    
    Args:
        email: El correo electrónico a buscar
        
    Returns:
        Un diccionario con los datos del usuario si se encuentra, None en caso contrario
    """
    return mongo.db.users.find_one({"email": email})

def save_user_to_db(user_dict: Dict[str, Any]) -> bool:
    """
    Guarda un usuario en la base de datos
    
    Args:
        user_dict: Diccionario con los datos del usuario
        
    Returns:
        True si se guardó correctamente, False en caso contrario
    """
    try:
        mongo.db.users.insert_one(user_dict)
        return True
    except Exception as e:
        current_app.logger.error(f"Error guardando usuario: {e}")
        return False


# RUTAS DE AUTENTICACIÓN

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registra un nuevo usuario en el sistema
    
    Requiere: username, email, password, role
    Retorna: mensaje de confirmación o error
    """
    try:
        data = request.get_json()
        
        # Validar datos
        required_fields = ("username", "email", "password", "role")
        if not data or not all(k in data for k in required_fields):
            return jsonify({"error": "Faltan datos"}), 400

        # Validar longitudes
        if len(data["username"]) < MIN_USERNAME_LENGTH:
            return jsonify({"error": "El nombre de usuario debe tener al menos 5 caracteres"}), 400
        if len(data["username"]) > MAX_USERNAME_LENGTH:
            return jsonify({"error": "Username demasiado largo"}), 400
        if len(data["email"]) > MAX_EMAIL_LENGTH:
            return jsonify({"error": "Email demasiado largo"}), 400
        if len(data["password"]) > MAX_PASSWORD_LENGTH:
            return jsonify({"error": "Contraseña demasiado larga"}), 400

        # Validar email
        if find_by_email(data["email"]):
            return jsonify({"error": "El usuario ya existe"}), 409

        # Crear usuario
        user = User(
            username=data["username"], 
            email=data["email"], 
            password=data["password"], 
            role=data["role"],
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", "")
        )
        user_dict = user.to_dict()
        
        if save_user_to_db(user_dict):
            return jsonify({"message": "Usuario registrado con éxito"}), 201
        else:
            return jsonify({"error": "Error al registrar usuario"}), 500

    except Exception as e:
        current_app.logger.error(f"[register] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Autentica a un usuario y genera un token JWT
    
    Requiere: email, password, remember_me (opcional)
    Retorna: token de acceso o mensaje de error
    """
    try:
        data = request.get_json()

        # Validar datos
        if not data or not all(k in data for k in ("email", "password")):
            return jsonify({"error": "Faltan datos"}), 400

        # Validar longitudes
        if len(data["email"]) > MAX_EMAIL_LENGTH or len(data["password"]) > MAX_PASSWORD_LENGTH:
            return jsonify({"error": "Datos demasiado largos"}), 400

        # Obtener el valor de remember_me (por defecto False)
        remember_me = data.get("remember_me", False)

        # Autenticar usuario
        user_data = find_by_email(data["email"])
        if user_data:
            user = User.from_dict(user_data)
            if user.check_password(data["password"]):
                # Configurar la duración del token basado en remember_me
                if remember_me:
                    expires = timedelta(days=30)  # 30 días si "recordarme" está marcado
                else:
                    expires = timedelta(hours=24)  # 24 horas por defecto
                
                token = create_access_token(
                    identity=user.email,
                    additional_claims={"role": user.role},
                    expires_delta=expires
                )
                return jsonify({
                    "access_token": token,
                    "remember_me": remember_me
                }), 200
        
        return jsonify({"error": "Credenciales incorrectas"}), 401

    except Exception as e:
        current_app.logger.error(f"[login] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

@auth_bp.route("/request-reset", methods=["POST"])
def request_password_reset():
    """
    Solicita el envío de un token para restablecer contraseña
    
    Requiere: email
    Retorna: token de restablecimiento o error
    """
    data = request.get_json()
    email = data.get("email")

    # Verifica el email enviado y el usuario en la base de datos
    if not email or not find_by_email(email):
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
@jwt_required()
def reset_password():
    """
    Cambia la contraseña si el token es válido
    
    Requiere: token, new_password
    Retorna: confirmación o error
    """
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

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Invalida el token actual (agrega a la lista negra)
    
    Requiere: JWT válido en cabecera
    Retorna: confirmación de cierre de sesión
    """
    try:
        jti = get_jwt()["jti"]  # JWT ID
        blacklist.add(jti)
        return jsonify({"message": "Sesión cerrada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al cerrar sesión"}), 500