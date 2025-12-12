import sentry_sdk
from models import db
from flask import Blueprint
from models.user import User
from utils.utils import get_response
from flask_restful import Api, Resource, reqparse
from flask_bcrypt import check_password_hash, generate_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_parse = reqparse.RequestParser()
auth_parse.add_argument("username", type=str, required=True, help="Username cannot be blank")
auth_parse.add_argument("password", type=str, required=True, help="Password cannot be blank")

profile_update_parse = reqparse.RequestParser()
profile_update_parse.add_argument("full_name", type=str)
profile_update_parse.add_argument("username", type=str)
profile_update_parse.add_argument("phone_number", type=str)
profile_update_parse.add_argument("pic_path", type=str)

change_password_parse = reqparse.RequestParser()
change_password_parse.add_argument("current_password", type=str, required=True, help="Current Password cannot be blank")
change_password_parse.add_argument("new_password", type=str, required=True, help="New Password cannot be blank")

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
api = Api(auth_bp)

class AuthResource(Resource):

    def post(self):
        """Auth Login API
        Path - /api/auth/login
        Method - POST
        ---
        consumes: application/json
        parameters:
            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    username: 
                        type: string
                    password:
                        type: string
                required: [username, password]
        responses:
            200:
                description: Return Access Token and Refresh Token
            404:
                description: Username or Password is Incorrect
            400:
                description: Username or Password is Blank
        """
        data = auth_parse.parse_args()
        username = data['username']
        password = data['password']
        sentry_sdk.logger.info(f"Login attempt for user: {username}")

        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            sentry_sdk.logger.warning(f"Login failed for user: {username} - User not found or inactive")
            return get_response("Username or Password is incorrect", None, 404), 404
        
        if not check_password_hash(user.password, password):
            sentry_sdk.logger.warning(f"Login failed for user: {username} - Incorrect password")
            return get_response("Username or Password is incorrect", None, 404), 404
        
        access_token = create_access_token(identity=user.username)
        refresh_token = create_refresh_token(identity=user.username)
        result_data = {
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        sentry_sdk.logger.info(f"User {username} logged in successfully")
        return get_response("Successfully Logged in!", result_data, 200), 200

class RefreshResource(Resource):
    decorators = [jwt_required(refresh=True)]

    def post(self):
        """Auth Refresh Token API
        Path - /api/auth/refresh
        Method - POST
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
                description: Return New Access Token
            404:
                description: User not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Refresh token attempt for user: {username}")

        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            sentry_sdk.logger.warning(f"Refresh token failed for user: {username} - User not found or not active")
            return get_response("User not found or not active", None, 404), 404
        
        new_access_token = create_access_token(identity=user.username)
        result_data = {
            "access_token": new_access_token,
        }
        sentry_sdk.logger.info(f"User {username} Refreshed token successfully")
        return get_response("Successfully Refreshed token!", result_data, 200), 200

class ProfileResource(Resource):
    decorators = [jwt_required()]

    def get(self):
        """Auth Profile Get API
        Path - /api/auth/profile/me
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
                description: Return a User
            404:
                description: User not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Profile get attempt for user: {username}")

        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            sentry_sdk.logger.warning(f"Profile get failed for user: {username} - User not found or not active")
            return get_response("User not found or not active", None, 404), 404
        
        sentry_sdk.logger.info(f"{username} - User successfully found")
        return get_response("User successfully found", user.to_dict(), 200), 200

    def post(self):
        """Auth Profile Post API
        Path - /api/auth/profile/me
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
                    full_name:
                        type: string
                    username:
                        type: string
                    phone_number:
                        type: string
                    pic_path:
                        type: string

        responses:
            200:
                description: Successfully updated user
            404:
                description: User not found or not active
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Profile post attempt for user: {username}")

        found_user = User.query.filter_by(username=username, is_active=True).first()
        if not found_user:
            sentry_sdk.logger.warning(f"Profile post failed for user: {username} - User not found or not active")
            return get_response("User not found or not active", None, 404), 404
        
        data = profile_update_parse.parse_args()
        full_name = data.get('full_name', None)
        in_username = data.get('username', None)
        phone_number = data.get('phone_number', None)
        pic_path = data.get('pic_path', None)

        if full_name is not None:
            sentry_sdk.logger.info(f"{username} - User full name update now.")
            found_user.full_name = full_name

        if in_username is not None:
            sentry_sdk.logger.info(f"{username} - User username update now.")
            found_user.username = in_username

        if phone_number is not None:
            sentry_sdk.logger.info(f"{username} - User phone number update now.")
            found_user.phone_number = phone_number

        if pic_path is not None:
            sentry_sdk.logger.info(f"{username} - User pic path update now.")
            found_user.pic_path = pic_path

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - User successfully updated")
        return get_response("Successfully updated user", None, 200), 200

class ChangePasswordResource(Resource):
    decorators = [jwt_required()]

    def post(self):
        """Auth Change Password API
        Path - /api/auth/change-password
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
                    current_password:
                        type: string
                    new_password:
                        type: string
                required: [current_password, new_password]
        responses:
            200:
                description: Successfully changed password
            404:
                description: User not found or not active
            400:
                description: (Current Password or New Password is Blank) or (Password Incorrec)
        """
        username = get_jwt_identity()
        sentry_sdk.logger.info(f"Change password attempt for user: {username}")

        found_user = User.query.filter_by(username=username, is_active=True).first()
        if not found_user:
            sentry_sdk.logger.warning(f"Change password failed for user: {username} - User not found or not active")
            return get_response("User not found or not active", None, 404), 404
        
        data = change_password_parse.parse_args()
        current_password = data['current_password']
        new_password = data['new_password']

        if not check_password_hash(found_user.password, current_password):
            sentry_sdk.logger.warning(f"Change password failed for user: {username} - Password Incorrect")
            return get_response("Password Incorrec", None, 400), 400

        sentry_sdk.logger.info(f"{username} - User password update now.")
        found_user.password = generate_password_hash(new_password).decode("utf-8")

        db.session.commit()
        sentry_sdk.logger.info(f"{username} - Successfully changed password")
        return get_response("Successfully changed password", None, 200), 200

api.add_resource(AuthResource, "/login")
api.add_resource(RefreshResource, "/refresh")
api.add_resource(ProfileResource, "/profile/me")
api.add_resource(ChangePasswordResource, "/change-password")
