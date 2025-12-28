import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Language(db.Model):
    __tablename__ = "language"

    id = db.Column(db.Integer(), primary_key=True)

    lang = db.Column(db.String(10), nullable=False)
    code = db.Column(db.Text(), nullable=False)
    message = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(), default=datetime.now(time_zone))

    def __init__(self, lang, code, message):
        super().__init__()
        self.lang = lang
        self.code = code
        self.message = message

    @staticmethod
    def to_dict(language):
        _ = {
            "id": language.id,
            "lang": language.lang,
            "code": language.code,
            "message": language.message,
            "created_at": str(language.created_at)
        }
        return _
