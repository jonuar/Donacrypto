from flask import Flask
from flask_cors import CORS
from .extensions import mongo, jwt
import logging
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from bson import ObjectId

load_dotenv()

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,  # Usar WARNING en producción
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Configurar encoder JSON personalizado para manejar datetime y ObjectId
    from flask.json.provider import DefaultJSONProvider
    
    class CustomJSONProvider(DefaultJSONProvider):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, ObjectId):
                return str(obj)
            return super().default(obj)
    
    app.json = CustomJSONProvider(app)

    # Config seguridad
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-development") #Quitar segundo parámetro para producción
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-jwt")
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

    # MongoDB config
    app.config["MONGO_URI"] = "mongodb://localhost:27017/db_plataforma_donaciones"

    # Inicializa extensiones
    mongo.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Importa y registra Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.user_routes import user_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix='/user')

    return app


#------------------------------------------------------------------------------------------------------------
#TODO


# {
#   "email": "joshuanunezarcila@gmail.com",
#   "password": "password123"
# }

# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0ODQ3ODUzMCwianRpIjoiNjhmM2Q5M2YtZTc2Yy00ZDQ2LTkxZDYtYWQxM2IzNGIxMmRjIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6Impvc2h1YW51bmV6YXJjaWxhQGdtYWlsLmNvbSIsIm5iZiI6MTc0ODQ3ODUzMCwiY3NyZiI6IjI0MmJmODBhLTA3ZjAtNGJiNS1hMjViLTk5Y2FjZTFjYjQ4YSIsImV4cCI6MTc0ODU2NDkzMCwicm9sZSI6ImZvbGxvd2VyIn0.Yc3o3fuen2Xnc-IiRw-Rh1KakQrUiPtX85M1C_4Ytow"
# }


# Creator: 
# email: nunezarcilajoshua@gmail.com
# username: hungry_artist
# password: password123