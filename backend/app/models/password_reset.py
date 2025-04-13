from datetime import datetime, timedelta
from flask  import current_app
from ..extensions import mongo

class PasswordResetToken:
    """Modelo para tokens de recuperación de contraseña"""

    @staticmethod
    def save_token(email, token, expires_in_minutes=30):
        expiration = datetime.now() + timedelta(minutes=expires_in_minutes)
        try:
            mongo.db.password_reset.insert_one({
                "email": email,
                "token": token,
                "expires_at": expiration
            })
            return True
        except Exception as e:
            return False

    @staticmethod
    def verify_token(token):
        try:
            result = mongo.db.password_reset.find_one({"token": token})
            if result and result["expires_at"] > datetime.now():
                return result["email"]
        except Exception as e:
            current_app.logger.error(f"Error verify_token: {e}")
        return None

    @staticmethod
    def delete_token(token):
        try:
            mongo.db.password_reset.delete_one({"token": token})
        except Exception:
            pass
