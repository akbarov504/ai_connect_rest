import sentry_sdk
from models import db
from flask import Blueprint
from models.company import Company
from utils.utils import get_response
from flask_restful import Api, Resource
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models.interaction_log import InteractionLog

interaction_log_bp = Blueprint("interaction_log", __name__, url_prefix="/api/interaction_log")
api = Api(interaction_log_bp)

class InteractionLogResource(Resource):
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, interaction_log_id):
        """InteractionLog Get API
        Path - /api/interaction_log/<interaction_log_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: interaction_log_id
              in: path
              type: integer
              required: true
              description: Enter InteractionLog ID
        responses:
            200:
                description: Return a InteractionLog
            404:
                description: InteractionLog not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"InteractionLog get attempt for user: {username}")

        interaction_log = InteractionLog.query.filter_by(id=interaction_log_id).first()
        if not interaction_log:
            sentry_sdk.logger.warning(f"InteractionLog get failed for user: {username} - InteractionLog not found")
            return get_response("InteractionLog not found", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - InteractionLog successfully found")
        return get_response("InteractionLog successfully found", interaction_log.to_dict(), 200), 200

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER"])
    def delete(self, interaction_log_id):
        """InteractionLog Delete API
        Path - /api/interaction_log/<interaction_log_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: interaction_log_id
              in: path
              type: integer
              required: true
              description: Enter InteractionLog ID
        responses:
            200:
                description: Delete a InteractionLog
            404:
                description: InteractionLog not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"InteractionLog delete attempt for user: {username}")

        interaction_log = InteractionLog.query.filter_by(id=interaction_log_id).first()
        if not interaction_log:
            sentry_sdk.logger.warning(f"InteractionLog delete failed for user: {username} - InteractionLog not found")
            return get_response("InteractionLog not found", None, 404), 404

        db.session.delete(interaction_log)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - InteractionLog successfully deleted")
        return get_response("Successfully deleted InteractionLog", None, 200), 200
    
class InteractionLogListResource(Resource):

    @role_required(["SUPERADMIN"])
    def get(self):
        """InteractionLog List API
        Path - /api/interaction_log
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
                description: Return InteractionLog List
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"InteractionLog list attempt for user: {username}")

        interaction_log_list = InteractionLog.query.filter_by().order_by(InteractionLog.created_at.desc()).all()
        result_interaction_log_list = [interaction_log.to_dict() for interaction_log in interaction_log_list]

        sentry_sdk.logger.info(f"{username} - InteractionLog list")
        return get_response("InteractionLog List", result_interaction_log_list, 200), 200

class InteractionLogCompanyListResource(Resource):

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """InteractionLog Company List API
        Path - /api/interaction_log/company/<company_id>
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
                description: Return InteractionLog List
            404:
                description: Company not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"InteractionLog user list attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id, is_active=True).first()
        if not found_company:
            sentry_sdk.logger.warning(f"InteractionLog user list failed for user: {username} - Company not found or not active")
            return get_response("Company not found or not active", None, 404), 404

        interaction_log_list = InteractionLog.query.filter_by(company_id=found_company.id).order_by(InteractionLog.created_at.desc()).all()
        result_interaction_log_list = [interaction_log.to_dict() for interaction_log in interaction_log_list]

        sentry_sdk.logger.info(f"{username} - InteractionLog user list")
        return get_response("InteractionLog User List", result_interaction_log_list, 200), 200

api.add_resource(InteractionLogResource, "/<interaction_log_id>")
api.add_resource(InteractionLogListResource, "/")
api.add_resource(InteractionLogCompanyListResource, "/company/<company_id>")
