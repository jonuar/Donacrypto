from typing import Dict, Any, List, Optional
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..extensions import mongo

def add_like_info_to_posts(posts: List[Dict[str, Any]], current_user_email: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Agrega información de likes a una lista de posts
    
    Args:
        posts: Lista de posts (diccionarios)
        current_user_email: Email del usuario actual (opcional)
    
    Returns:
        Lista de posts con información de likes agregada
    """
    if not posts:
        return posts
    
    # Si no se proporciona email del usuario, intentar obtenerlo del JWT
    if current_user_email is None:
        try:
            verify_jwt_in_request(optional=True)
            current_user_email = get_jwt_identity()
        except:
            pass
    
    # Obtener todos los post_ids
    post_ids = [str(post.get("_id", "")) for post in posts]
    
    # Obtener todos los likes de estos posts en una sola consulta
    likes_data = list(mongo.db.likes.find({"post_id": {"$in": post_ids}}))
    
    # Organizar likes por post_id
    likes_by_post = {}
    user_likes = set()
    
    for like in likes_data:
        post_id = like["post_id"]
        if post_id not in likes_by_post:
            likes_by_post[post_id] = 0
        likes_by_post[post_id] += 1
        
        # Marcar si el usuario actual le dio like
        if current_user_email and like["user_email"] == current_user_email:
            user_likes.add(post_id)
    
    # Agregar información de likes a cada post
    for post in posts:
        post_id = str(post.get("_id", ""))
        post["likes_count"] = likes_by_post.get(post_id, 0)
        post["user_liked"] = post_id in user_likes
    
    return posts
