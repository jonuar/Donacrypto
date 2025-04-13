from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime, timedelta
from flask import current_app
from ..extensions import mongo

class User:
    """Modelo de usuario para la autenticación y operaciones en MongoDB"""

    def __init__(self, username, email, password, role="follower", is_hashed=False):
        self.username = username
        self.email = email
        self.role = role
        self.password_hash = password if is_hashed else generate_password_hash(password)

    def save_to_db(self):
        """Guarda el usuario en MongoDB"""
        try:
            mongo.db.users.insert_one({
                "username": self.username,
                "email": self.email,
                "role": self.role,
                "password": self.password_hash,
                "created_at": datetime.now()
            })
        except Exception as e:
            current_app.logger.error(f"[save_to_db] Error al guardar usuario: {e}")
            return None
        return self

    @staticmethod
    def find_by_email(email):
        """Busca un usuario por su email"""
        try:
            current_app.logger.info(f"Buscando usuario con email: {email}")
            user_data = mongo.db.users.find_one({"email": email})
            if user_data:
                current_app.logger.info(f"Usuario encontrado: {user_data['email']}, Role: {user_data['role']}")
                return User(user_data["username"], user_data["email"], user_data["password"], user_data["role"], is_hashed=True)
        except Exception as e:
            current_app.logger.error(f"[find_by_email] Error al buscar usuario: {e}")
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_token(self):
        return create_access_token(identity=self.email, expires_delta=timedelta(hours=24))
