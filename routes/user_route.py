import sentry_sdk
from models import db
from flask import Blueprint
from models.user import User
from models.company import Company
from utils.utils import get_response
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api, Resource, reqparse
from utils.decorators import role_required, super_admin_required

user_create_parse = reqparse.RequestParser()
user_create_parse.add_argument("company_id", type=int, required=True, help="Company ID cannot be blank")
user_create_parse.add_argument("full_name", type=str, required=True, help="Full Name cannot be blank")
user_create_parse.add_argument("username", type=str, required=True, help="Username cannot be blank")
user_create_parse.add_argument("phone_number", type=str, required=True, help="Phone Number cannot be blank")
user_create_parse.add_argument("role", type=str, required=True, help="Role cannot be blank")
user_create_parse.add_argument("password", type=str, required=True, help="Password cannot be blank")
user_create_parse.add_argument("pic_path", type=str)

user_update_parse = reqparse.RequestParser()
user_update_parse.add_argument("company_id", type=int)
user_update_parse.add_argument("full_name", type=str)
user_update_parse.add_argument("username", type=str)
user_update_parse.add_argument("phone_number", type=str)
user_update_parse.add_argument("role", type=str)
user_update_parse.add_argument("password", type=str)
user_update_parse.add_argument("pic_path", type=str)
user_update_parse.add_argument("is_active", type=bool)

user_bp = Blueprint("user", __name__, url_prefix="/api/user")
api = Api(user_bp)

class UserResource(Resource):
    
    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, user_id):
        """User Get API
        Path - /api/user/<user_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: user_id
              in: path
              type: integer
              required: true
              description: Enter User ID
        responses:
            200:
                description: Return a User
            404:
                description: User not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"User get attempt for user: {username}")

        user = User.query.filter_by(id=user_id).first()
        if not user:
            sentry_sdk.logger.warning(f"User get failed for user: {username} - User not found")
            return get_response("User not found", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - User successfully found")
        return get_response("User successfully found", user.to_dict(), 200), 200

    @super_admin_required()
    def delete(self, user_id):
        """User Delete API
        Path - /api/user/<user_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: user_id
              in: path
              type: integer
              required: true
              description: Enter User ID
        responses:
            200:
                description: Delete a User
            404:
                description: User not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"User delete attempt for user: {username}")

        user = User.query.filter_by(id=user_id, is_superadmin=False).first()
        if not user:
            sentry_sdk.logger.warning(f"User delete failed for user: {username} - User not found")
            return get_response("User not found", None, 404), 404

        db.session.delete(user)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - User successfully deleted")
        return get_response("Successfully deleted User", None, 200), 200
    
    @role_required(["SUPERADMIN", "ADMIN"])
    def patch(self, user_id):
        """User Update API
        Path - /api/user/<user_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: user_id
              in: path
              type: integer
              required: true
              description: Enter User ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    company_id: 
                        type: integer
                    full_name:
                        type: string
                    username:
                        type: string
                    phone_number:
                        type: string
                    role:
                        type: string
                    password:
                        type: string
                    pic_path:
                        type: string
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated user
            404:
                description: User not found
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"User update attempt for user: {username}")

        user = User.query.filter_by(username=username, is_superadmin=True).first()

        found_user = User.query.filter_by(id=user_id, is_superadmin=False).first()
        if not found_user:
            sentry_sdk.logger.warning(f"User update failed for user: {username} - User not found")
            return get_response("User not found", None, 404), 404
        
        data = user_update_parse.parse_args()
        company_id = data.get('company_id', None)
        full_name = data.get('full_name', None)
        in_username = data.get('username', None)
        phone_number = data.get('phone_number', None)
        role = data.get('role', None)
        password = data.get('password', None)
        pic_path = data.get('pic_path', None)
        is_active = data.get('is_active', None)

        if company_id is not None and user is not None:
            sentry_sdk.logger.info(f"{username} - User company id update now.")
            found_user.company_id = company_id

        if full_name is not None:
            sentry_sdk.logger.info(f"{username} - User full name update now.")
            found_user.full_name = full_name

        if in_username is not None:
            sentry_sdk.logger.info(f"{username} - User username update now.")
            found_user.username = in_username

        if phone_number is not None:
            sentry_sdk.logger.info(f"{username} - User phone number update now.")
            found_user.phone_number = phone_number

        if role is not None:
            sentry_sdk.logger.info(f"{username} - User role update now.")
            found_user.role = role

        if password is not None:
            sentry_sdk.logger.info(f"{username} - User password update now.")
            found_user.password = generate_password_hash(password).decode("utf-8")

        if pic_path is not None:
            sentry_sdk.logger.info(f"{username} - User pic path update now.")
            found_user.pic_path = pic_path

        if is_active is not None:
            sentry_sdk.logger.info(f"{username} - User is active update now.")
            found_user.is_active = is_active

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - User successfully updated")
        return get_response("Successfully updated user", None, 200), 200

class UserListCreateResource(Resource):

    @role_required(["SUPERADMIN"])
    def get(self):
        """User List API
        Path - /api/user
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
                description: Return User List
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"User list attempt for user: {username}")

        user_list = User.query.filter_by().order_by(User.created_at.desc()).all()
        result_user_list = [user.to_dict() for user in user_list]

        sentry_sdk.logger.info(f"{username} - User list")
        return get_response("User List", result_user_list, 200), 200

    @role_required(["SUPERADMIN", "ADMIN"])
    def post(self):
        """User Create API
        Path - /api/user
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
                    full_name:
                        type: string
                    username:
                        type: string
                    phone_number:
                        type: string
                    role:
                        type: string
                    password:
                        type: string
                    pic_path:
                        type: string
                required: [company_id, full_name, username, phone_number, role, password]
        responses:
            200:
                description: Return New User ID
            400:
                description: (Company ID, Full Name, Username, Phone Number, Role or Password is Blank) or (Username already taken or Phone Number already taken)
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"User create attempt for user: {username}")

        data = user_create_parse.parse_args()
        company_id = data['company_id']
        full_name = data['full_name']
        in_username = data['username']
        phone_number = data['phone_number']
        role = data['role']
        password = data['password']
        pic_path = data.get('pic_path', None)

        user = User.query.filter_by(username=in_username).first()
        if user:
            sentry_sdk.logger.warning(f"User create failed for user: {username} - User Username already exists")
            return get_response("Username already exists", None, 400), 400
        
        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            sentry_sdk.logger.warning(f"User create failed for user: {username} - User Phone Number already exists")
            return get_response("Phone Number already exists", None, 400), 400
        
        new_user = User(company_id, full_name, in_username, phone_number, role, password, is_superadmin=False, pic_path=pic_path)
        db.session.add(new_user)
        db.session.commit()

        sentry_sdk.logger.info(f"{username} - User successfully created")
        return get_response("Successfully created user", new_user.id, 200), 200

class UserCompanyListResource(Resource):

    @role_required(["SUPERADMIN", "ADMIN", "MANAGER", "OPERATOR"])
    def get(self, company_id):
        """User Company List API
        Path - /api/user/company/<company_id>
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
                description: Return User List
            404:
                description: Company not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"User user list attempt for user: {username}")

        found_company = Company.query.filter_by(id=company_id, is_active=True).first()
        if not found_company:
            sentry_sdk.logger.warning(f"User user list failed for user: {username} - Company not found or not active")
            return get_response("Company not found or not active", None, 404), 404

        user_list = User.query.filter_by(company_id=found_company.id).order_by(User.created_at.desc()).all()
        result_user_list = [user.to_dict() for user in user_list]

        sentry_sdk.logger.info(f"{username} - User user list")
        return get_response("User User List", result_user_list, 200), 200

api.add_resource(UserResource, "/<user_id>")
api.add_resource(UserListCreateResource, "/")
api.add_resource(UserCompanyListResource, "/company/<company_id>")
