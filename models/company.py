import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Company(db.Model):
    __tablename__ = "company"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    contact_email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    instagram_id = db.Column(db.String(50), nullable=False)
    instagram_token = db.Column(db.Text(), nullable=False)
    openai_token = db.Column(db.Text(), nullable=False)
    logo_path = db.Column(db.Text, nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(), default=datetime.now(time_zone))

    def __init__(self, title, description, contact_number, contact_email, address, instagram_id, instagram_token, openai_token, logo_path=None):
        super().__init__()
        self.title = title
        self.description = description
        self.contact_number = contact_number
        self.contact_email = contact_email
        self.address = address
        self.instagram_id = instagram_id
        self.instagram_token = instagram_token
        self.openai_token = openai_token
        if logo_path is None or logo_path == "":
            self.logo_path = "https://firebasestorage.googleapis.com/v0/b/kamronlessonbot.appspot.com/o/aiconnect%2Fcompany_logo%2Fcompany_default_logo.png?alt=media&token=cafaf6b1-240c-4890-abdf-4cc66e575156"
        else:
            self.logo_path = logo_path

    def __repr__(self):
        return f"<Company {self.title}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "contact_number": self.contact_number,
            "contact_email": self.contact_email,
            "address": self.address,
            "instagram_id": self.instagram_id,
            "instagram_token": self.instagram_token,
            "openai_token": self.openai_token,
            "logo_path": self.logo_path,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
