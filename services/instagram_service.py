import sentry_sdk
import os, requests
from models import db
from celery import shared_task
from models.company import Company
from models.company_lid import CompanyLid
from models.interaction_log import InteractionLog
from services.ai_service import get_ai_reply, get_full_name, get_phone_number

URL = os.getenv("IG_API_URL")

@shared_task
def send_dm_reply(sender_id, message, company_id):
    company = Company.query.filter_by(id=company_id).first()
    url = f"{URL}/me/messages?access_token={company.instagram_token}"

    sentry_sdk.logger.warning(f"Instagram webhook post send_dm_reply = sender_id - {sender_id}, company_id - {company_id}, message - {message}")
    payload = {
        "recipient": {"id": sender_id},
        "messaging_type": "RESPONSE",
        "message": {"text": message},
    }

    requests.post(url, json=payload)
    sentry_sdk.logger.warning(f"Instagram webhook post send_dm_reply successfully sended")

def get_dm_username(sender_id, company_id):
    company = Company.query.filter_by(id=company_id).first()
    url = f"{URL}/{sender_id}?fields=username&access_token={company.instagram_token}"

    sentry_sdk.logger.warning(f"Instagram webhook post get_dm_username = sender_id - {sender_id}, company_id - {company_id}, token - {company.instagram_token}")
    result = requests.get(url).json()

    sentry_sdk.logger.warning(f"Instagram webhook post get_dm_username = username - {result['username']}")
    return result["username"]

@shared_task(name="services.instagram_service.process_dm")
def process_dm(message, sender_id, company_id):
    print(message)
    user_username = get_dm_username(sender_id, company_id)

    found_company_lid = CompanyLid.query.filter_by(company_id=company_id, user_instagram_id=sender_id, username=user_username).first()
    if not found_company_lid:
        found_company_lid = CompanyLid(company_id, sender_id, user_username, "NEW")
        db.session.add(found_company_lid)

    have_full_name = False
    have_phone_number = False

    if found_company_lid.full_name is None:
        send_full_name = get_full_name(message, company_id)
        print(send_full_name)
        if send_full_name != "no":
            have_full_name = True
            found_company_lid.full_name = send_full_name
        else:
            have_full_name = False
    
    if found_company_lid.phone_number is None:
        send_phone_number = get_phone_number(message, company_id)
        print(send_phone_number)
        if send_phone_number != "no":
            have_phone_number = True
            found_company_lid.phone_number = send_phone_number
        else:
            have_phone_number = False

    ai_response = get_ai_reply(message, company_id, have_full_name, have_phone_number)

    new_interaction_log = InteractionLog(company_id, sender_id, user_username, "DIRECT", message, ai_response)
    db.session.add(new_interaction_log)
    db.session.commit()

    sentry_sdk.logger.warning(f"Instagram webhook post process_dm - {new_interaction_log.id}")
    send_dm_reply.delay(sender_id, ai_response, company_id)
