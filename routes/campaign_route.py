import sentry_sdk
from models import db
from flask import Blueprint
from models.user import User
from models.company import Company
from models.campaign import Campaign
from utils.utils import get_response
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api, Resource, reqparse

campaign_create_parse = reqparse.RequestParser()
campaign_create_parse.add_argument("company_id", type=int, required=True, help="Company ID cannot be blank")
campaign_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
campaign_create_parse.add_argument("content", type=str, required=True, help="Content cannot be blank")

campaign_update_parse = reqparse.RequestParser()
campaign_update_parse.add_argument("company_id", type=int)
campaign_update_parse.add_argument("title", type=str)
campaign_update_parse.add_argument("content", type=str)
campaign_update_parse.add_argument("is_active", type=bool)

campaign_bp = Blueprint("campaign", __name__, url_prefix="/api/campaign")
api = Api(campaign_bp)

class CampaignResource(Resource):
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def get(self, campaign_id):
        """Campaign Get API
        Path - /api/campaign/<campaign_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: campaign_id
              in: path
              type: integer
              required: true
              description: Enter Campaign ID
        responses:
            200:
                description: Return a Campaign
            404:
                description: Campaign not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Campaign get attempt for user: {username}")

        campaign = Campaign.query.filter_by(id=campaign_id).first()
        if not campaign:
            sentry_sdk.logger.warning(f"Campaign get failed for user: {username} - Campaign not found")
            return get_response("Campaign not found", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - Campaign successfully found")
        return get_response("Campaign successfully found", campaign.to_dict(), 200), 200

    @role_required(["SUPERADMIN", "ADMIN"])
    def delete(self, campaign_id):
        """Campaign Delete API
        Path - /api/campaign/<campaign_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: campaign_id
              in: path
              type: integer
              required: true
              description: Enter Campaign ID
        responses:
            200:
                description: Delete a Campaign
            404:
                description: Campaign not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Campaign delete attempt for user: {username}")

        campaign = Campaign.query.filter_by(id=campaign_id).first()
        if not campaign:
            sentry_sdk.logger.warning(f"Campaign delete failed for user: {username} - Campaign not found")
            return get_response("Campaign not found", None, 404), 404

        db.session.delete(campaign)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - Campaign successfully deleted")
        return get_response("Successfully deleted campaign", None, 200), 200
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def patch(self, campaign_id):
        """Campaign Update API
        Path - /api/campaign/<campaign_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: campaign_id
              in: path
              type: integer
              required: true
              description: Enter Campaign ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    company_id: 
                        type: integer
                    title:
                        type: string
                    content:
                        type: string
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated campaign
            404:
                description: Campaign not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Campaign update attempt for user: {username}")

        user = User.query.filter_by(username=username, is_superadmin=True).first()

        found_campaign = Campaign.query.filter_by(id=campaign_id).first()
        if not found_campaign:
            sentry_sdk.logger.warning(f"Campaign update failed for user: {username} - Campaign not found")
            return get_response("Campaign not found", None, 404), 404
        
        data = campaign_update_parse.parse_args()
        company_id = data.get('company_id', None)
        title = data.get('title', None)
        content = data.get('content', None)
        is_active = data.get('is_active', None)

        if company_id is not None and user is not None:
            sentry_sdk.logger.info(f"{username} - Campaign company id update now.")
            found_campaign.company_id = company_id

        if title is not None:
            sentry_sdk.logger.info(f"{username} - Campaign title update now.")
            found_campaign.title = title

        if content is not None:
            sentry_sdk.logger.info(f"{username} - Campaign content update now.")
            found_campaign.content = content

        if is_active is not None:
            sentry_sdk.logger.info(f"{username} - Campaign is active update now.")
            found_campaign.is_active = is_active

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - Campaign successfully updated")
        return get_response("Successfully updated campaign", None, 200), 200

class CampaignListCreateResource(Resource):

    @role_required(["SUPERADMIN"])
    def get(self):
        """Campaign List API
        Path - /api/campaign
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

        responses:
            200:
                description: Return Campaign List
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Campaign list attempt for user: {username}")

        campaign_list = Campaign.query.filter_by().order_by(Campaign.created_at.desc()).all()
        result_campaign_list = [campaign.to_dict() for campaign in campaign_list]

        sentry_sdk.logger.info(f"{username} - Campaign list")
        return get_response("Campaign List", result_campaign_list, 200), 200

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def post(self):
        """Campaign Create API
        Path - /api/campaign
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    company_id: 
                        type: integer
                    title:
                        type: string
                    content:
                        type: string
                required: [company_id, title, content]
        responses:
            200:
                description: Return New Campaign ID
            400:
                description: Company ID, Title or Content is Blank
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Campaign create attempt for user: {username}")

        data = campaign_create_parse.parse_args()
        company_id = data['company_id']
        title = data['title']
        content = data['content']
        
        new_campaign = Campaign(company_id, title, content)
        db.session.add(new_campaign)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - Campaign successfully created")
        return get_response("Successfully created campaign", new_campaign.id, 200), 200

class CampaignUserListResource(Resource):

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """Campaign User List API
        Path - /api/campaign/user/<company_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: company_id
              in: path
              type: integer
              required: true
              description: Enter Company ID
              
        responses:
            200:
                description: Return Campaign List
            404:
                description: Company not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Campaign user list attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id, is_active=True).first()
        if not found_company:
            sentry_sdk.logger.warning(f"Campaign user list failed for user: {username} - Company not found or not active")
            return get_response("Company not found or not active", None, 404), 404

        campaign_list = Campaign.query.filter_by(company_id=found_company.id).order_by(Campaign.created_at.desc()).all()
        result_campaign_list = [campaign.to_dict() for campaign in campaign_list]

        sentry_sdk.logger.info(f"{username} - Campaign user list")
        return get_response("Campaign User List", result_campaign_list, 200), 200

api.add_resource(CampaignResource, "/<campaign_id>")
api.add_resource(CampaignListCreateResource, "/")
api.add_resource(CampaignUserListResource, "/user/<company_id>")
