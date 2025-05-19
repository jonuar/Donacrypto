from flask import jsonify, current_app
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from ..models.user import User

# Decorador para verificar el rol del usuario
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                # Obtener email desde el JWT
                identity = get_jwt_identity()
                current_app.logger.info(f"JWT Identity: {identity}")

                # Buscar usuario por email
                user = User.find_by_email(identity)
                current_app.logger.info(f"User found: {user.username if user else 'None'}, Role: {user.role if user else 'None'}")

                # Validar rol
                if not user or user.role != required_role:
                    return jsonify({"error": "No tienes permisos para acceder a esta ruta"}), 403

                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Error en role_required: {e}")
                return jsonify({"error": f"Error en la validación del rol: {str(e)}"}), 500
        return decorated
    return wrapper
