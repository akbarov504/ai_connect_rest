import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class InteractionLog(db.Model):
    __tablename__ = "interaction_log"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, nullable=False)
    user_instagram_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    interaction_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(time_zone))

    def __init__(self, company_id, user_instagram_id, username, interaction_type, message, ai_response):
        super().__init__()
        self.company_id = company_id
        self.user_instagram_id = user_instagram_id
        self.username = username
        self.interaction_type = interaction_type
        self.message = message
        self.ai_response = ai_response

    def __repr__(self):
        return f"<InteractionLog {self.username}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_instagram_id": self.user_instagram_id,
            "username": self.username,
            "interaction_type": self.interaction_type,
            "message": self.message,
            "ai_response": self.ai_response,
            "created_at": self.created_at.isoformat()
        }
