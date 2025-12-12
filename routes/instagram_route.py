import os
import sentry_sdk
from models.company import Company
from utils.utils import get_response
from flask_restful import Api, Resource
from flask import Blueprint, Response, request
from services.instagram_service import process_dm

VERIFY_TOKEN = os.getenv("IG_VERIFY_TOKEN")

instagram_bp = Blueprint("instagram", __name__)
api = Api(instagram_bp)

class InstagramResource(Resource):
    def get(self):
        mode = request.args.get("hub.mode")
        challenge = request.args.get("hub.challenge")
        token = request.args.get("hub.verify_token")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            sentry_sdk.logger.info(f"Instagram webhook verification successfully")
            return Response(str(challenge), 200)

        sentry_sdk.logger.warning(f"Instagram webhook verification failed")
        return "Verification failed", 403

    def post(self):
        data = request.json
        sentry_sdk.logger.warning(f"Instagram webhook post data - {data}")
        try:
            entry = data["entry"][0]
            messaging = entry["messaging"][0]

            message = messaging["message"]['text']
            sender_id = messaging["sender"]['id']

            is_echo = messaging["message"].get("is_echo", None)
            if is_echo:
                return {"status": "ok"}, 200

            instagram_id = entry["id"]
            found_company = Company.query.filter_by(instagram_id=instagram_id).first()
            if not found_company:
                sentry_sdk.logger.warning(f"Instagram webhook failed - Company not found")
                return get_response("Company not found", None, 404), 404

            sentry_sdk.logger.warning(f"Instagram webhook post = message - {message}, sender_id - {sender_id}, company_id - {found_company.id}")
            process_dm.delay(message, sender_id, found_company.id)
            return {"status": "ok"}, 200

        except Exception as e:
            sentry_sdk.logger.error(f"Instagram webhook post error - {str(e)}")
            return {"error": str(e)}, 200

api.add_resource(InstagramResource, "/webhook/instagram")
