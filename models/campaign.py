import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Campaign(db.Model):
    __tablename__ = "campaign"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(time_zone))

    def __init__(self, company_id, title, content):
        super().__init__()
        self.company_id = company_id
        self.title = title
        self.content = content

    def __repr__(self):
        return f"<Campaign {self.title}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "title": self.title,
            "content": self.content,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
