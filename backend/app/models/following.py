from datetime import datetime
from typing import Dict, Any, Optional

class Following:
    """Modelo para gestionar la relación de seguimiento entre follower y creator"""

    def __init__(self, follower_email: str, creator_email: str, created_at: Optional[datetime] = None) -> None:
        """
        Args:
            follower_email: Email del usuario con role='follower'
            creator_email: Email del usuario con role='creator' que es seguido
            created_at: Fecha de creación de la relación (opcional)
        """
        self.follower_email: str = follower_email
        self.creator_email: str = creator_email
        self.created_at: datetime = created_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario para persistencia"""
        return {
            "follower_email": self.follower_email,
            "creator_email": self.creator_email,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Following':
        """Crea una instancia desde un diccionario"""
        return cls(
            follower_email=data["follower_email"],
            creator_email=data["creator_email"],
            created_at=data.get("created_at", datetime.now())
        )