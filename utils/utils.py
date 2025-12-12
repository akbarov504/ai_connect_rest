import os
from dotenv import load_dotenv

def get_response(message, result, status_code):
    _ = {
        "message": message,
        "result": result,
        "status_code": status_code
    }
    return _

def super_admin_create():
    from models import db
    from models.user import User
    from models.company import Company

    load_dotenv()

    found_company = Company.query.filter_by(title="AiConnect").first()
    if not found_company:
        ai_connect_company = Company("AiConnect", "AiConnect Company", "+998909380018", "akbarovakbar888@gmail.com", "Uzbekistan, Tashkent, Alisher Navoi, 35.", os.getenv("IG_ID"), os.getenv("IG_ACCESS_TOKEN"), os.getenv("OPENAI_API_KEY"), logo_path="https://firebasestorage.googleapis.com/v0/b/kamronlessonbot.appspot.com/o/aiconnect%2Fcompany_logo%2Fai_connect_logo.png?alt=media&token=e6ad1d3e-d00e-49c7-8fab-98f60d94e8a6")
        db.session.add(ai_connect_company)
        db.session.commit()
        print("Successfully created AiConnect company, Akbarov.")
    
    found_user = User.query.filter_by(username="akbarov504", phone_number="+998909380018").first()
    if not found_user:
        super_admin = User(ai_connect_company.id, os.getenv("SUPERADMIN_FULL_NAME"), os.getenv("SUPERADMIN_USERNAME"), os.getenv("SUPERADMIN_PHONE"), "SUPERADMIN", os.getenv("SUPERADMIN_PASSWORD"), is_superadmin=True)
        db.session.add(super_admin)
        db.session.commit()
        print("Successfully created Super Admin, Akbarov.")

    return None
