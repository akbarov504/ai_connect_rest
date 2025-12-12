import sentry_sdk
from flask import Blueprint
from models.user import User
from datetime import datetime
from models.company import Company
from utils.utils import get_response
from flask_restful import Api, Resource
from models.company_lid import CompanyLid
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models.interaction_log import InteractionLog

main_bp = Blueprint("main", __name__, url_prefix="/api/main/dashboard")
api = Api(main_bp)

class MainResource(Resource):
    
    @role_required(["SUPERADMIN"])
    def get(self):
        """Main Dashboard Get API
        Path - /api/main/dashboard
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
                description: Return a Main Dashboard
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Main Dashboard get attempt for user: {username}")

        user_list = User.query.filter_by(is_active=True).all()
        company_list = Company.query.filter_by(is_active=True).all()
        company_lid_list = CompanyLid.query.all()
        interaction_list = InteractionLog.query.all()
        interaction_dm_list = InteractionLog.query.filter_by(interaction_type="DIRECT").all()
        interaction_comment_list = InteractionLog.query.filter_by(interaction_type="COMMENT").all()

        now_time = datetime.now()
        now_date = datetime(now_time.year, now_time.month, now_time.day)
        interaction_now_list = InteractionLog.query.filter(InteractionLog.created_at.between(now_date, now_time)).all()

        result = {
            "user_count": len(user_list),
            "company_count": len(company_list),
            "company_lid_count": len(company_lid_list),
            "interaction_count": len(interaction_list),
            "interaction_dm_count": len(interaction_dm_list),
            "interaction_comment_count": len(interaction_comment_list),
            "interaction_now_count": len(interaction_now_list) 
        }
        
        sentry_sdk.logger.info(f"{username} - Main Dashboard successfully found")
        return get_response("Main Dashboard successfully found", result, 200), 200

class MainUserResource(Resource):

    @role_required(["ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """Main Dashboard User Get API
        Path - /api/main/dashboard/user/<company_id>
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
                description: Return a Main Dashboard User
            404:
                description: Company not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Main Dashboard User get attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id, is_active=True).first()
        if not found_company:
            sentry_sdk.logger.warning(f"Main Dashboard User failed for user: {username} - Company not found")
            return get_response("Company not found", None, 404), 404

        user_list = User.query.filter_by(company_id=found_company.id, is_active=True).all()
        company_list = Company.query.filter_by(id=found_company.id, is_active=True).all()
        company_lid_list = CompanyLid.query.filter_by(company_id=found_company.id).all()
        interaction_list = InteractionLog.query.filter_by(company_id=found_company.id).all()
        interaction_dm_list = InteractionLog.query.filter_by(company_id=found_company.id, interaction_type="DIRECT").all()
        interaction_comment_list = InteractionLog.query.filter_by(company_id=found_company.id, interaction_type="COMMENT").all()

        now_time = datetime.now()
        now_date = datetime(now_time.year, now_time.month, now_time.day)
        interaction_now_list = InteractionLog.query.filter_by(company_id=found_company.id).filter(InteractionLog.created_at.between(now_date, now_time)).all()

        result = {
            "user_count": len(user_list),
            "company_count": len(company_list),
            "company_lid_count": len(company_lid_list),
            "interaction_count": len(interaction_list),
            "interaction_dm_count": len(interaction_dm_list),
            "interaction_comment_count": len(interaction_comment_list),
            "interaction_now_count": len(interaction_now_list) 
        }
        
        sentry_sdk.logger.info(f"{username} - Main Dashboard User successfully found")
        return get_response("Main Dashboard User successfully found", result, 200), 200

api.add_resource(MainResource, "/")
api.add_resource(MainUserResource, "/user/<company_id>")
