import sentry_sdk
from models import db
from flask import Blueprint
from models.user import User
from models.company import Company
from utils.utils import get_response
from models.ai_config import AiConfig
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api, Resource, reqparse

ai_config_create_parse = reqparse.RequestParser()
ai_config_create_parse.add_argument("company_id", type=int, required=True, help="Company ID cannot be blank")
ai_config_create_parse.add_argument("template_name", type=str, required=True, help="Template Name cannot be blank")
ai_config_create_parse.add_argument("template_text", type=str, required=True, help="Template Text cannot be blank")
ai_config_create_parse.add_argument("use_openai", type=bool, required=True, help="Use OpenAi cannot be blank")

ai_config_update_parse = reqparse.RequestParser()
ai_config_update_parse.add_argument("company_id", type=int)
ai_config_update_parse.add_argument("template_name", type=str)
ai_config_update_parse.add_argument("template_text", type=str)
ai_config_update_parse.add_argument("use_openai", type=bool)

ai_config_bp = Blueprint("ai_config", __name__, url_prefix="/api/ai_config")
api = Api(ai_config_bp)

class AiConfigResource(Resource):
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, ai_config_id):
        """AiConfig Get API
        Path - /api/ai_config/<ai_config_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: ai_config_id
              in: path
              type: integer
              required: true
              description: Enter AiConfig ID
        responses:
            200:
                description: Return a AiConfig
            404:
                description: AiConfig not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"AiConfig get attempt for user: {username}")

        ai_config = AiConfig.query.filter_by(id=ai_config_id).first()
        if not ai_config:
            sentry_sdk.logger.warning(f"AiConfig get failed for user: {username} - AiConfig not found")
            return get_response("AiConfig not found", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - AiConfig successfully found")
        return get_response("AiConfig successfully found", ai_config.to_dict(), 200), 200

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def delete(self, ai_config_id):
        """AiConfig Delete API
        Path - /api/ai_config/<ai_config_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: ai_config_id
              in: path
              type: integer
              required: true
              description: Enter AiConfig ID
        responses:
            200:
                description: Delete a AiConfig
            404:
                description: AiConfig not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"AiConfig delete attempt for user: {username}")

        ai_config = AiConfig.query.filter_by(id=ai_config_id).first()
        if not ai_config:
            sentry_sdk.logger.warning(f"AiConfig delete failed for user: {username} - AiConfig not found")
            return get_response("AiConfig not found", None, 404), 404

        db.session.delete(ai_config)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - AiConfig successfully deleted")
        return get_response("Successfully deleted AiConfig", None, 200), 200
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def patch(self, ai_config_id):
        """AiConfig Update API
        Path - /api/ai_config/<ai_config_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: ai_config_id
              in: path
              type: integer
              required: true
              description: Enter AiConfig ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    company_id: 
                        type: integer
                    template_name:
                        type: string
                    template_text:
                        type: string
                    use_openai:
                        type: boolean
        responses:
            200:
                description: Successfully updated AiConfig
            404:
                description: AiConfig not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"AiConfig update attempt for user: {username}")

        user = User.query.filter_by(username=username, is_superadmin=True).first()

        found_ai_config = AiConfig.query.filter_by(id=ai_config_id).first()
        if not found_ai_config:
            sentry_sdk.logger.warning(f"AiConfig update failed for user: {username} - AiConfig not found")
            return get_response("AiConfig not found", None, 404), 404
        
        data = ai_config_update_parse.parse_args()
        company_id = data.get('company_id', None)
        template_name = data.get('template_name', None)
        template_text = data.get('template_text', None)
        use_openai = data.get('use_openai', None)

        if company_id is not None and user is not None:
            sentry_sdk.logger.info(f"{username} - AiConfig company id update now.")
            found_ai_config.company_id = company_id

        if template_name is not None:
            sentry_sdk.logger.info(f"{username} - AiConfig template name update now.")
            found_ai_config.template_name = template_name

        if template_text is not None:
            sentry_sdk.logger.info(f"{username} - AiConfig template text update now.")
            found_ai_config.template_text = template_text

        if use_openai is not None:
            sentry_sdk.logger.info(f"{username} - AiConfig use openai update now.")
            found_ai_config.use_openai = use_openai

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - AiConfig successfully updated")
        return get_response("Successfully updated AiConfig", None, 200), 200

class AiConfigListCreateResource(Resource):

    @role_required(["SUPERADMIN"])
    def get(self):
        """AiConfig List API
        Path - /api/ai_config
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
                description: Return AiConfig List
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"AiConfig list attempt for user: {username}")

        ai_config_list = AiConfig.query.filter_by().order_by(AiConfig.created_at.desc()).all()
        result_ai_config_list = [ai_config.to_dict() for ai_config in ai_config_list]

        sentry_sdk.logger.info(f"{username} - AiConfig list")
        return get_response("AiConfig List", result_ai_config_list, 200), 200

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def post(self):
        """AiConfig Create API
        Path - /api/ai_config
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
                    template_name:
                        type: string
                    template_text:
                        type: string
                    use_openai:
                        type: boolean
                required: [company_id, template_name, template_text, use_openai]
        responses:
            200:
                description: Return New AiConfig ID
            400:
                description: Company ID, Template Name, Template Text or Use OpenAi is Blank
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"AiConfig create attempt for user: {username}")

        data = ai_config_create_parse.parse_args()
        company_id = data['company_id']
        template_name = data['template_name']
        template_text = data['template_text']
        use_openai = data['use_openai']
        
        new_ai_config = AiConfig(company_id, template_name, template_text, use_openai)
        db.session.add(new_ai_config)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - AiConfig successfully created")
        return get_response("Successfully created AiConfig", new_ai_config.id, 200), 200

class AiConfigCompanyListResource(Resource):

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """AiConfig Company List API
        Path - /api/ai_config/company/<company_id>
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
                description: Return AiConfig List
            404:
                description: Company not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"AiConfig user list attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id, is_active=True).first()
        if not found_company:
            sentry_sdk.logger.warning(f"AiConfig user list failed for user: {username} - Company not found or not active")
            return get_response("Company not found or not active", None, 404), 404

        ai_config_list = AiConfig.query.filter_by(company_id=found_company.id).order_by(AiConfig.created_at.desc()).all()
        result_ai_config_list = [ai_config.to_dict() for ai_config in ai_config_list]

        sentry_sdk.logger.info(f"{username} - AiConfig user list")
        return get_response("AiConfig User List", result_ai_config_list, 200), 200

api.add_resource(AiConfigResource, "/<ai_config_id>")
api.add_resource(AiConfigListCreateResource, "/")
api.add_resource(AiConfigCompanyListResource, "/company/<company_id>")
