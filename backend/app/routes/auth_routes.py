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
def register() -> Tuple[Any, int]:
    """
    Registra un nuevo usuario en el sistema
    
    Requiere: username, email, password, role
    Retorna: mensaje de confirmación o error
    """
    try:
        data: Dict[str, Any] = request.get_json()

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
        if find_by_email(data["email"]):
            return jsonify({"error": "El usuario ya existe"}), 409

        # Crear usuario
        user: User = User(data["username"], data["email"], data["password"], data["role"])
        user_dict: Dict[str, Any] = user.to_dict()
        
        if save_user_to_db(user_dict):
            return jsonify({"message": "Usuario registrado con éxito"}), 201
        else:
            return jsonify({"error": "Error al registrar usuario"}), 500

    except Exception as e:
        current_app.logger.error(f"[register] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500


@auth_bp.route("/login", methods=["POST"])
def login() -> Tuple[Any, int]:
    """
    Autentica a un usuario y genera un token JWT
    
    Requiere: email, password
    Retorna: token de acceso o mensaje de error
    """
    try:
        data: Dict[str, Any] = request.get_json()

        # Validar datos
        if not data or not all(k in data for k in ("email", "password")):
            return jsonify({"error": "Faltan datos"}), 400

        # Validar longitudes
        if len(data["email"]) > MAX_EMAIL_LENGTH or len(data["password"]) > MAX_PASSWORD_LENGTH:
            return jsonify({"error": "Datos demasiado largos"}), 400

        # Autenticar usuario
        user_data: Optional[Dict[str, Any]] = find_by_email(data["email"])
        if user_data:
            user: User = User.from_dict(user_data)
            if user.check_password(data["password"]):
                expires: timedelta = timedelta(hours=24)
                token: str = create_access_token(
                    identity=user.email,
                    additional_claims={"role": user.role},
                    expires_delta=expires
                )
                return jsonify({"access_token": token}), 200
        
        return jsonify({"error": "Credenciales incorrectas"}), 401

    except Exception as e:
        current_app.logger.error(f"[login] Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500
    

@auth_bp.route("/request-reset", methods=["POST"])
def request_password_reset() -> Tuple[Any, int]:
    """
    Solicita el envío de un token para restablecer contraseña
    
    Requiere: email
    Retorna: token de restablecimiento o error
    """
    data: Dict[str, Any] = request.get_json()
    email: Optional[str] = data.get("email")

    # Verifica el email enviado y el usuario en la base de datos
    if not email or not find_by_email(email):
        return jsonify({"error": "Email no registrado"}), 404

    # Genera un token único y seguro para el restablecimiento de contraseña
    token: str = secrets.token_urlsafe(32)
    
    # Guarda el token en la base de datos con una fecha de expiración
    if PasswordResetToken.save_token(email, token):
        # El token puede ser enviado por correo, o simplemente devolverlo si es para frontend
        return jsonify({"message": "Token generado", "reset_token": token}), 200
    else:
        return jsonify({"error": "Error generando token"}), 500

@auth_bp.route("/reset-password", methods=["POST"])
@jwt_required()
def reset_password() -> Tuple[Any, int]:
    """
    Cambia la contraseña si el token es válido
    
    Requiere: token, new_password
    Retorna: confirmación o error
    """
    data: Dict[str, Any] = request.get_json()
    token: Optional[str] = data.get("token")
    new_password: Optional[str] = data.get("new_password")

    # Verifica que ambos campos (token y nueva contraseña) estén presentes
    if not token or not new_password:
        return jsonify({"error": "Datos incompletos"}), 400

    # Verifica si el token es válido y no ha expirado
    email: Optional[str] = PasswordResetToken.verify_token(token)
    if not email:
        return jsonify({"error": "Token inválido o expirado"}), 400

    # Si el token es válido, cambia la contraseña
    try:
        # Cifra la nueva contraseña
        hashed_password: str = generate_password_hash(new_password)
        # Actualiza la contraseña del usuario en la base de datos
        mongo.db.users.update_one({"email": email}, {"$set": {"password": hashed_password}})
        # Elimina el token después de usarlo para evitar su reutilización
        PasswordResetToken.delete_token(token)
        
        return jsonify({"message": "Contraseña actualizada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error actualizando contraseña"}), 500 

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout() -> Tuple[Any, int]:
    """
    Invalida el token actual (agrega a la lista negra)
    
    Requiere: JWT válido en cabecera
    Retorna: confirmación de cierre de sesión
    """
    try:
        jti: str = get_jwt()["jti"]  # JWT ID
        blacklist.add(jti)
        return jsonify({"message": "Sesión cerrada correctamente"}), 200
    except Exception as e:
        return jsonify({"error": "Error al cerrar sesión"}), 500