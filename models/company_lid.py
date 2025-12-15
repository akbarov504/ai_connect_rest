import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class CompanyLid(db.Model):
    __tablename__ = "company_lid"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, nullable=False)
    user_instagram_id = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    when_call = db.Column(db.Text, nullable=True)
    interest = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, company_id, user_instagram_id, username, status):
        super().__init__()
        self.company_id = company_id
        self.user_instagram_id = user_instagram_id
        self.username = username
        self.status = status

    def __repr__(self):
        return f"<Company Lid {self.full_name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_instagram_id": self.user_instagram_id,
            "username": self.username,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "when_call": self.when_call,
            "interest": self.interest,
            "status": self.status,
            "message": self.message,
            "created_at": self.created_at.isoformat()
        }
