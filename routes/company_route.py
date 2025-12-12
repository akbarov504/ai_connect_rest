import sentry_sdk
from models import db
from flask import Blueprint
from models.user import User
from models.company import Company
from models.campaign import Campaign
from utils.utils import get_response
from models.ai_config import AiConfig
from flask_jwt_extended import get_jwt_identity
from models.interaction_log import InteractionLog
from flask_restful import Api, Resource, reqparse
from utils.decorators import role_required, super_admin_required

company_create_parse = reqparse.RequestParser()
company_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
company_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
company_create_parse.add_argument("contact_number", type=str, required=True, help="Contact Number cannot be blank")
company_create_parse.add_argument("contact_email", type=str, required=True, help="Contact Email cannot be blank")
company_create_parse.add_argument("address", type=str, required=True, help="Address cannot be blank")
company_create_parse.add_argument("instagram_id", type=str, required=True, help="Instagram ID cannot be blank")
company_create_parse.add_argument("instagram_token", type=str, required=True, help="Instagram Token cannot be blank")
company_create_parse.add_argument("openai_token", type=str, required=True, help="OpenAi Token cannot be blank")
company_create_parse.add_argument("logo_path", type=str)

company_update_parse = reqparse.RequestParser()
company_update_parse.add_argument("title", type=str)
company_update_parse.add_argument("description", type=str)
company_update_parse.add_argument("contact_number", type=str)
company_update_parse.add_argument("contact_email", type=str)
company_update_parse.add_argument("address", type=str)
company_update_parse.add_argument("instagram_id", type=str)
company_update_parse.add_argument("instagram_token", type=str)
company_update_parse.add_argument("openai_token", type=str)
company_update_parse.add_argument("logo_path", type=str)
company_update_parse.add_argument("is_active", type=bool)

company_bp = Blueprint("company", __name__, url_prefix="/api/company")
api = Api(company_bp)

class CompanyResource(Resource):
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """Company Get API
        Path - /api/company/<company_id>
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
                description: Return a Company
            404:
                description: Company not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Company get attempt for user: {username}")

        company = Company.query.filter_by(id=company_id).first()
        if not company:
            sentry_sdk.logger.warning(f"Company get failed for user: {username} - Company not found")
            return get_response("Company not found", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - Company successfully found")
        return get_response("Company successfully found", company.to_dict(), 200), 200

    @super_admin_required()
    def delete(self, company_id):
        """Company Delete API
        Path - /api/company/<company_id>
        Method - DELETE
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
                description: Delete a Company
            404:
                description: Company not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Company delete attempt for user: {username}")

        company = Company.query.filter_by(id=company_id).first()
        if not company:
            sentry_sdk.logger.warning(f"Company delete failed for user: {username} - Company not found")
            return get_response("Company not found", None, 404), 404
        
        sentry_sdk.logger.info(f"Company delete user list attempt for user: {username}")
        user_list = User.query.filter_by(company_id=company.id).all()
        for user in user_list:
            db.session.delete(user)
        
        sentry_sdk.logger.info(f"Company delete campaign list attempt for user: {username}")
        campaign_list = Campaign.query.filter_by(company_id=company.id).all()
        for campaign in campaign_list:
            db.session.delete(campaign)
        
        sentry_sdk.logger.info(f"Company delete ai config list attempt for user: {username}")
        ai_config_list = AiConfig.query.filter_by(company_id=company.id).all()
        for ai_config in ai_config_list:
            db.session.delete(ai_config)
        
        sentry_sdk.logger.info(f"Company delete interaction log list attempt for user: {username}")
        interaction_log_list = InteractionLog.query.filter_by(company_id=company.id).all()
        for interaction_log in interaction_log_list:
            db.session.delete(interaction_log)

        db.session.delete(company)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - Company successfully deleted")
        return get_response("Successfully deleted company", None, 200), 200
    
    @role_required(["SUPERADMIN", "ADMIN"])
    def patch(self, company_id):
        """Company Update API
        Path - /api/company/<company_id>
        Method - PATCH
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

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    title: 
                        type: string
                    description:
                        type: string
                    contact_number:
                        type: string
                    contact_email:
                        type: string
                    address:
                        type: string
                    instagram_id:
                        type: string
                    instagram_token:
                        type: string
                    openai_token:
                        type: string
                    logo_path:
                        type: string
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated company
            404:
                description: Company not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Company update attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id).first()
        if not found_company:
            sentry_sdk.logger.warning(f"Company update failed for user: {username} - Company not found")
            return get_response("Company not found", None, 404), 404
        
        data = company_update_parse.parse_args()
        title = data.get('title', None)
        description = data.get('description', None)
        contact_number = data.get('contact_number', None)
        contact_email = data.get('contact_email', None)
        address = data.get('address', None)
        instagram_id = data.get('instagram_id', None)
        instagram_token = data.get('instagram_token', None)
        openai_token = data.get('openai_token', None)
        logo_path = data.get('logo_path', None)
        is_active = data.get('is_active', None)

        if title is not None:
            sentry_sdk.logger.info(f"{username} - Company title update now.")
            found_company.title = title

        if description is not None:
            sentry_sdk.logger.info(f"{username} - Company description update now.")
            found_company.description = description

        if contact_number is not None:
            sentry_sdk.logger.info(f"{username} - Company contact number update now.")
            found_company.contact_number = contact_number

        if contact_email is not None:
            sentry_sdk.logger.info(f"{username} - Company contact email update now.")
            found_company.contact_email = contact_email

        if address is not None:
            sentry_sdk.logger.info(f"{username} - Company address update now.")
            found_company.address = address
        
        if instagram_id is not None:
            sentry_sdk.logger.info(f"{username} - Company instagram id update now.")
            found_company.instagram_id = instagram_id

        if instagram_token is not None:
            sentry_sdk.logger.info(f"{username} - Company instagram token update now.")
            found_company.instagram_token = instagram_token

        if openai_token is not None:
            sentry_sdk.logger.info(f"{username} - Company openai token update now.")
            found_company.openai_token = openai_token

        if logo_path is not None:
            sentry_sdk.logger.info(f"{username} - Company logo path update now.")
            found_company.logo_path = logo_path

        if is_active is not None:
            sentry_sdk.logger.info(f"{username} - Company is active update now.")
            found_company.is_active = is_active

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - Company successfully updated")
        return get_response("Successfully updated company", None, 200), 200

class CompanyListCreateResource(Resource):

    @role_required(["SUPERADMIN"])
    def get(self):
        """Company List API
        Path - /api/company
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
                description: Return Company List
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Company list attempt for user: {username}")

        company_list = Company.query.filter_by().order_by(Company.created_at.desc()).all()
        result_company_list = [company.to_dict() for company in company_list]

        sentry_sdk.logger.info(f"{username} - Company list")
        return get_response("Company List", result_company_list, 200), 200

    @super_admin_required()
    def post(self):
        """Company Create API
        Path - /api/company
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
                    title: 
                        type: string
                    description:
                        type: string
                    contact_number:
                        type: string
                    contact_email:
                        type: string
                    address:
                        type: string
                    instagram_id:
                        type: string
                    instagram_token:
                        type: string
                    openai_token:
                        type: string
                    logo_path:
                        type: string
                required: [title, description, contact_number, contact_email, address, instagram_id, instagram_token, openai_token]
        responses:
            200:
                description: Return New Company ID
            400:
                description: (Title, Description, Contact Number, Contact Email, Address Instagram ID, Instagram Token or OpenAi Token is Blank) or (Title already taken)
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Company create attempt for user: {username}")

        data = company_create_parse.parse_args()
        title = data['title']
        description = data['description']
        contact_number = data['contact_number']
        contact_email = data['contact_email']
        address = data['address']
        instagram_id = data['instagram_id']
        instagram_token = data['instagram_token']
        openai_token = data['openai_token']
        logo_path = data.get('logo_path', None)

        company = Company.query.filter_by(title=title).first()
        if company:
            sentry_sdk.logger.warning(f"Company create failed for user: {username} - Company Title already exists")
            return get_response("Title already exists", None, 400), 400
        
        new_company = Company(title, description, contact_number, contact_email, address, instagram_id, instagram_token, openai_token, logo_path)
        db.session.add(new_company)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - Company successfully created")
        return get_response("Successfully created company", new_company.id, 200), 200

class CompanyUserListResource(Resource):

    @role_required(["ADMIN", "MANAGER", "OPERATOR"])
    def get(self):
        """Company User List API
        Path - /api/company/user
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
                description: Return Company List
            404:
                description: User not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Company user list attempt for user: {username}")

        found_user = User.query.filter_by(username=username, is_active=True).first()
        if not found_user:
            sentry_sdk.logger.warning(f"Company user list failed for user: {username} - User not found or not active")
            return get_response("User not found or not active", None, 404), 404

        company_list = Company.query.filter_by(id=found_user.company_id).order_by(Company.created_at.desc()).all()
        result_company_list = [company.to_dict() for company in company_list]

        sentry_sdk.logger.info(f"{username} - Company user list")
        return get_response("Company User List", result_company_list, 200), 200

api.add_resource(CompanyResource, "/<company_id>")
api.add_resource(CompanyListCreateResource, "/")
api.add_resource(CompanyUserListResource, "/user")
