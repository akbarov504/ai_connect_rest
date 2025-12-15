import os
from flask import Flask

from models.user import User
from models.company import Company
from models.campaign import Campaign
from models.ai_config import AiConfig
from models.company_lid import CompanyLid
from models.interaction_log import InteractionLog

from dotenv import load_dotenv
from utils.utils import super_admin_create
from utils.openai_config import init_openai
from utils.celery_config import make_celery
from utils.sentry_config import init_sentry_sdk
from utils.redis_client_config import init_redis_client
from models import db, migrate, bcrypt, jwt, cors, limiter, swagger

from routes.auth_route import auth_bp
from routes.user_route import user_bp
from routes.main_route import main_bp
from routes.company_route import company_bp
from routes.campaign_route import campaign_bp
from routes.ai_config_route import ai_config_bp
from routes.instagram_route import instagram_bp
from routes.company_lid_route import company_lid_bp
from routes.interaction_log_route import interaction_log_bp

load_dotenv()

app = Flask(__name__)
app.config["DEBUG"] = bool(os.getenv("APP_DEBUG"))
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_pre_ping": True,
    "pool_recycle": 300
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = bool(os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS"))
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES"))
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES"))
app.config["RATELIMIT_HEADERS_ENABLED"] = bool(os.getenv("RATELIMIT_HEADERS_ENABLED"))
app.config["RATELIMIT_STRATEGY"] = os.getenv("RATELIMIT_STRATEGY")
app.config["RATELIMIT_STORAGE_URL"] = os.getenv("RATE_LIMIT_STORAGE_URL")

db.init_app(app)
migrate.init_app(app, db)
bcrypt.init_app(app)
jwt.init_app(app)
limiter.init_app(app)
swagger.init_app(app)
cors.init_app(app, origins=os.getenv("CORS_ALLOWED_ORIGINS"))

celery = make_celery(app)
redis_client = init_redis_client()
sentry_sdk = init_sentry_sdk()
openai_client = init_openai()

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(main_bp)
app.register_blueprint(company_bp)
app.register_blueprint(campaign_bp)
app.register_blueprint(ai_config_bp)
app.register_blueprint(instagram_bp)
app.register_blueprint(company_lid_bp)
app.register_blueprint(interaction_log_bp)

with app.app_context():
    db.create_all()
    super_admin_create()

if __name__ == '__main__':
    app.run(host=os.getenv("APP_HOST"), port=int(os.getenv("APP_PORT")))
