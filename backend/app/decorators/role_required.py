from flask import jsonify, current_app
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

# Decorador optimizado para verificar el rol del usuario usando solo JWT
def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            try:
                # Verificar que existe un JWT válido (esto reemplaza a @jwt_required())
                verify_jwt_in_request()
                
                # Obtener el claim 'role' directamente del JWT
                claims = get_jwt()
                user_role = claims.get("role")
                print(f"JWT Claims: {claims}")
                print(f"JWT Role: {user_role}")
                
                current_app.logger.info(f"JWT Role: {user_role}")
                
                # Validar rol
                if not user_role or user_role != required_role:
                    return jsonify({"error": "No tienes permisos para acceder a esta ruta"}), 403

                return fn(*args, **kwargs)
            except Exception as e:
                current_app.logger.error(f"Error en role_required: {e}")
                return jsonify({"error": f"Error en la validación del rol: {str(e)}"}), 500
        return decorated
    return wrapper
