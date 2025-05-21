from datetime import datetime
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from ..extensions import mongo

class User:
    """Modelo de usuario"""

    def __init__(self, username: str, email: str, password: str, role: str = "follower", is_hashed: bool = False) -> None:
        self.username: str = username
        self.email: str = email
        self.role: str = role
        self.password_hash: str = password if is_hashed else generate_password_hash(password)
        self.created_at: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario para persistencia"""
        return {
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "password": self.password_hash,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Crea una instancia desde un diccionario"""
        return cls(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            role=data["role"],
            is_hashed=True
        )

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña coincide"""
        return check_password_hash(self.password_hash, password)