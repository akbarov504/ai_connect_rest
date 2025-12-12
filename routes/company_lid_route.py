import sentry_sdk
from models import db
from flask import Blueprint
from models.company import Company
from utils.utils import get_response
from models.company_lid import CompanyLid
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api, Resource, reqparse

company_lid_update_parse = reqparse.RequestParser()
company_lid_update_parse.add_argument("status", type=str)
company_lid_update_parse.add_argument("message", type=str)

company_lid_bp = Blueprint("company_lid", __name__, url_prefix="/api/company_lid")
api = Api(company_lid_bp)

class CompanyLidResource(Resource):
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_lid_id):
        """CompanyLid Get API
        Path - /api/company_lid/<company_lid_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: company_lid_id
              in: path
              type: integer
              required: true
              description: Enter CompanyLid ID
        responses:
            200:
                description: Return a CompanyLid
            404:
                description: CompanyLid not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"CompanyLid get attempt for user: {username}")

        company_lid = CompanyLid.query.filter_by(id=company_lid_id).first()
        if not company_lid:
            sentry_sdk.logger.warning(f"CompanyLid get failed for user: {username} - CompanyLid not found")
            return get_response("CompanyLid not found", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - CompanyLid successfully found")
        return get_response("CompanyLid successfully found", company_lid.to_dict(), 200), 200
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def patch(self, company_lid_id):
        """CompanyLid Update API
        Path - /api/company_lid/<company_lid_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: company_lid_id
              in: path
              type: integer
              required: true
              description: Enter CompanyLid ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    status:
                        type: string
                    message:
                        type: string
        responses:
            200:
                description: Successfully updated company_lid
            404:
                description: CompanyLid not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"CompanyLid update attempt for user: {username}")

        found_company_lid = CompanyLid.query.filter_by(id=company_lid_id).first()
        if not found_company_lid:
            sentry_sdk.logger.warning(f"CompanyLid update failed for user: {username} - CompanyLid not found")
            return get_response("CompanyLid not found", None, 404), 404
        
        data = company_lid_update_parse.parse_args()
        status = data.get('status', None)
        message = data.get('message', None)

        if status is not None:
            sentry_sdk.logger.info(f"{username} - CompanyLid status update now.")
            found_company_lid.status = status
        
        if message is not None:
            sentry_sdk.logger.info(f"{username} - CompanyLid message update now.")
            found_company_lid.message = message

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - CompanyLid successfully updated")
        return get_response("Successfully updated company_lid", None, 200), 200

class CompanyLidListResource(Resource):

    @role_required(["SUPERADMIN"])
    def get(self):
        """CompanyLid List API
        Path - /api/company_lid
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
                description: Return CompanyLid List
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"CompanyLid list attempt for user: {username}")

        company_lid_list = CompanyLid.query.filter_by().order_by(CompanyLid.created_at.desc()).all()
        result_company_lid_list = [company_lid.to_dict() for company_lid in company_lid_list]

        sentry_sdk.logger.info(f"{username} - CompanyLid list")
        return get_response("CompanyLid List", result_company_lid_list, 200), 200

class CompanyLidUserListResource(Resource):

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """CompanyLid User List API
        Path - /api/company_lid/user/<company_id>
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
                description: Return CompanyLid List
            404:
                description: Company not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"CompanyLid user list attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id, is_active=True).first()
        if not found_company:
            sentry_sdk.logger.warning(f"CompanyLid user list failed for user: {username} - Company not found or not active")
            return get_response("Company not found or not active", None, 404), 404

        company_lid_list = CompanyLid.query.filter_by(company_id=found_company.id).order_by(CompanyLid.created_at.desc()).all()
        result_company_lid_list = [company_lid.to_dict() for company_lid in company_lid_list]

        sentry_sdk.logger.info(f"{username} - CompanyLid user list")
        return get_response("CompanyLid User List", result_company_lid_list, 200), 200

api.add_resource(CompanyLidResource, "/<company_lid_id>")
api.add_resource(CompanyLidListResource, "/")
api.add_resource(CompanyLidUserListResource, "/user/<company_id>")
