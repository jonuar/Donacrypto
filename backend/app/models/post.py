from datetime import datetime
from typing import Dict, Any, List, Optional

class Post:
    """Modelo para las publicaciones de los creadores"""

    def __init__(
        self,
        creator_email: str,
        content: str,
        title: str,
        media_urls: Optional[List[str]] = None
    ) -> None:
        self.creator_email: str = creator_email
        self.title: str = title
        self.content: str = content
        self.media_urls: List[str] = media_urls or []
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = self.created_at
        self.likes_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el objeto a diccionario para persistencia"""
        return {
            "creator_email": self.creator_email,
            "title": self.title,
            "content": self.content,
            "media_urls": self.media_urls,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "likes_count": self.likes_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        """Crea una instancia desde un diccionario"""
        post = cls(
            creator_email=data["creator_email"],
            title=data["title"],
            content=data["content"],
            media_urls=data.get("media_urls", [])
        )
        post.created_at = data.get("created_at", datetime.now())
        post.updated_at = data.get("updated_at", post.created_at)
        post.likes_count = data.get("likes_count", 0)
        return post