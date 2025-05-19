from datetime import datetime
from typing import Dict, Any, List

class Following:
    """Modelo para gestionar la lista de creadores seguidos por cada follower"""

    def __init__(self, follower_email: str, creator_list: List[Dict[str, Any]] = None) -> None:
        """
        Args:
            follower_email: Email del usuario con role='follower'
            creator_list: Lista de creadores seguidos
        """
        self.follower_email: str = follower_email
        self.creator_list: List[Dict[str, Any]] = creator_list or []
        self.updated_at: datetime = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario para persistencia"""
        return {
            "follower_email": self.follower_email,
            "creator_list": self.creator_list,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Following':
        """Crea una instancia desde un diccionario"""
        return cls(
            follower_email=data["follower_email"],
            creator_list=data.get("creator_list", [])
        )