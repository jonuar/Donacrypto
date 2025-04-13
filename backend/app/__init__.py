from flask import Flask
from flask_cors import CORS
from .extensions import mongo, jwt
import logging
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Usar WARNING en producción
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)

    # Config seguridad
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-development") #Quitar segundo parámetro para producción
    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY", "clave-secreta-jwt")
    app.config["JWT_BLACKLIST_ENABLED"] = True
    app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]

    # MONGODB config
    app.config["MONGO_URI"] = "mongodb://localhost:27017/db_plataforma_donaciones"

    # Inicializa extensiones
    mongo.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Importa y registra Blueprints
    from .routes.auth_routes import auth_bp
    from .routes.donation_routes import donation_bp
    from .routes.creator_routes import creator_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(donation_bp, url_prefix="/donations")
    app.register_blueprint(creator_bp)

    return app


#------------------------------------------------------------------------------------------------------------
#TODO

# 🪙 Integración de wallet / Hardhat / Metamask para facilitar donaciones reales.
# Usar librerías como web3.py o ethers.js para interactuar con contratos inteligentes.
# Usar libreria de terceros como Coinbase Commerce 


# Revisitar datos de /register tras crear frontend

# Validación más robusta (opcional)
# Usar librerías como pydantic, marshmallow o Cerberus para validar payloads

# Tests básicos (opcional pero recomendado):
# Usar pytest o unittest para probar login, registro, donaciones

# Documentación de la API:
# Agrega documentación tipo Swagger (usando Flask-Swagger o Postman exportado)
# O simplemente crea un README.md con todos los endpoints

# 📧 Recuperación de contraseña con token temporal o vía correo:
# Cómo enviar correo de recuperación?
# (Opcional) Integración con un servicio de correo o frontend para mostrar un modal
# puedes usar Flask-Mail o un servicio como SendGrid, Mailgun, o SMTP.

# Como registrar followers y creadores? (En Frontend)