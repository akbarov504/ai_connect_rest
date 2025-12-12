import os
from dotenv import load_dotenv
from flask_cors import CORS
from flasgger import Swagger
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter.util import get_remote_address

load_dotenv()

cors = CORS(supports_credentials=True, origins=["*"])
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()
migrate = Migrate()
swagger = Swagger(template={
    "info": {
        "title": "Ai Connect API",
        "description": "API documentation for Ai Connect platform",
        "version": "1.0.0"
    }
})
limiter = Limiter(key_func=get_remote_address, storage_uri=os.getenv("RATE_LIMIT_STORAGE_URL"), default_limits=[os.getenv("RATE_LIMIT_DEFAULT")])
