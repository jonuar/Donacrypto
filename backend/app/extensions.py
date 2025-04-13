from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager

mongo = PyMongo()

jwt = JWTManager()
blacklist = set()
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist
