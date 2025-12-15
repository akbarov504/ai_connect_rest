import pytz
from models import db
from datetime import datetime
from flask_bcrypt import generate_password_hash

time_zone = pytz.timezone("Asia/Tashkent")

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)
    is_superadmin = db.Column(db.Boolean, default=False)
    password = db.Column(db.Text, nullable=False)
    pic_path = db.Column(db.Text, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, company_id, full_name, username, phone_number, role, password, is_superadmin=False, pic_path=None):
        super().__init__()
        self.company_id = company_id
        self.full_name = full_name
        self.username = username
        self.phone_number = phone_number
        self.role = role
        self.password = generate_password_hash(password).decode("utf-8")
        self.is_superadmin = is_superadmin
        if pic_path is None or pic_path == "":
            self.pic_path = "https://firebasestorage.googleapis.com/v0/b/kamronlessonbot.appspot.com/o/aiconnect%2Fprofile_pic%2Fprofile_pic_default.jpg?alt=media&token=16ef7f25-c58f-4010-8682-daa83e10e229"
        else:
            self.pic_path = pic_path

    def __repr__(self):
        return f"<User {self.username}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "full_name": self.full_name,
            "username": self.username,
            "phone_number": self.phone_number,
            "role": self.role,
            "is_superadmin": self.is_superadmin,
            "pic_path": self.pic_path,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat()
        }
