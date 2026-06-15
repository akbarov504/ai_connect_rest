import os
import requests
import sentry_sdk
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

    sentry_sdk.logger.warning(
        f"send_dm_reply | sender_id={sender_id} | company_id={company_id} | message={message!r}"
    )

    payload = {
        "recipient": {"id": sender_id},
        "messaging_type": "RESPONSE",
        "message": {"text": message},
    }
    requests.post(url, json=payload)
    sentry_sdk.logger.warning("send_dm_reply | sent successfully")

def get_dm_username(sender_id, company_id):
    company = Company.query.filter_by(id=company_id).first()
    url = f"{URL}/{sender_id}?fields=username&access_token={company.instagram_token}"

    sentry_sdk.logger.warning(
        f"get_dm_username | sender_id={sender_id} | company_id={company_id}"
    )
    result = requests.get(url).json()
    username = result.get("username", sender_id)
    sentry_sdk.logger.warning(f"get_dm_username | username={username!r}")
    return username

@shared_task(name="services.instagram_service.process_dm")
def process_dm(message, sender_id, company_id, mid=None):
    sentry_sdk.logger.warning(
        f"process_dm | sender_id={sender_id} | company_id={company_id} | mid={mid} | message={message!r}"
    )

    if mid:
        already = InteractionLog.query.filter_by(
            company_id=company_id,
            message_id=mid
        ).first()
        if already:
            sentry_sdk.logger.warning(f"process_dm | DUPLICATE mid={mid} — skipped")
            return

    user_username = get_dm_username(sender_id, company_id)
    found_company_lid = CompanyLid.query.filter_by(
        company_id=company_id,
        user_instagram_id=sender_id
    ).first()

    if not found_company_lid:
        found_company_lid = CompanyLid(company_id, sender_id, user_username, "NEW")
        db.session.add(found_company_lid)
        db.session.flush()

    if found_company_lid.username != user_username:
        found_company_lid.username = user_username

    have_full_name = found_company_lid.full_name is not None
    have_phone_number = found_company_lid.phone_number is not None

    if not have_full_name:
        extracted_name = get_full_name(message, company_id)
        if extracted_name != "no":
            found_company_lid.full_name = extracted_name
            have_full_name = True
            if found_company_lid.phone_number:
                found_company_lid.status = "NEW"

    if not have_phone_number:
        extracted_phone = get_phone_number(message, company_id)
        if extracted_phone != "no":
            found_company_lid.phone_number = extracted_phone
            have_phone_number = True
            if found_company_lid.full_name:
                found_company_lid.status = "NEW"

    ai_response = get_ai_reply(
        sender_id, message, company_id,
        have_full_name, have_phone_number
    )

    new_log = InteractionLog(company_id, sender_id, user_username, "DIRECT", message, ai_response, mid)
    db.session.add(new_log)
    db.session.commit()

    sentry_sdk.logger.warning(f"process_dm | log_id={new_log.id} | reply={ai_response!r}")

    send_dm_reply.delay(sender_id, ai_response, company_id)
