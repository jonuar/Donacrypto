from datetime import datetime
from typing import Dict, Any, Optional

class Like:
    """Modelo para los likes de posts"""
    
    def __init__(self, user_email: str, post_id: str):
        self.user_email = user_email
        self.post_id = post_id
        self.created_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el like a diccionario para MongoDB"""
        return {
            "user_email": self.user_email,
            "post_id": self.post_id,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Like':
        """Crea una instancia de Like desde un diccionario"""
        like = cls.__new__(cls)
        like.user_email = data["user_email"]
        like.post_id = data["post_id"]
        like.created_at = data.get("created_at", datetime.utcnow())
        return like
