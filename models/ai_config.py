import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class AiConfig(db.Model):
    __tablename__ = "ai_config"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, nullable=False)
    template_name = db.Column(db.String(255), nullable=False)
    template_text = db.Column(db.Text, nullable=False)
    use_openai = db.Column(db.Boolean, nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, company_id, template_name, template_text, use_openai):
        super().__init__()
        self.company_id = company_id
        self.template_name = template_name
        self.template_text = template_text
        self.use_openai = use_openai

    def __repr__(self):
        return f"<Ai Config {self.template_name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "template_name": self.template_name,
            "template_text": self.template_text,
            "use_openai": self.use_openai,
            "created_at": self.created_at.isoformat()
        }
