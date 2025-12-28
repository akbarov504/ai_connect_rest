from models import db
from flask import Blueprint
from utils.utils import get_response
from models.language import Language
from utils.decorators import super_admin_required
from flask_restful import Api, Resource, reqparse

language_create_parse = reqparse.RequestParser()
language_create_parse.add_argument("lang", type=str, required=True, help="Lang cannot be blank")
language_create_parse.add_argument("code", type=str, required=True, help="Code cannot be blank")
language_create_parse.add_argument("message", type=str, required=True, help="Message cannot be blank")

language_update_parse = reqparse.RequestParser()
language_update_parse.add_argument("lang", type=str)
language_update_parse.add_argument("code", type=str)
language_update_parse.add_argument("message", type=str)

language_bp = Blueprint("language", __name__, url_prefix="/api/language")
api = Api(language_bp)

class LanguageResource(Resource):
    decorators = [super_admin_required()]
    
    def get(self, language_id):
        """Language Get API
        Path - /api/language/<language_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: language_id
              in: path
              type: integer
              required: true
              description: Enter Language ID
        responses:
            200:
                description: Return a Language
            404:
                description: Language not found
        """
        language = Language.query.filter_by(id=language_id).first()
        if not language:
            return get_response("Language not found", None, 404), 404
        
        return get_response("Language successfully found", Language.to_dict(language), 200), 200

    def delete(self, language_id):
        """Language Delete API
        Path - /api/language/<language_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: language_id
              in: path
              type: integer
              required: true
              description: Enter Language ID
        responses:
            200:
                description: Delete a Language
            404:
                description: Language not found
        """
        language = Language.query.filter_by(id=language_id).first()
        if not language:
            return get_response("Language not found", None, 404), 404
        
        db.session.delete(language)
        db.session.commit()
        return get_response("Successfully deleted language", None, 200), 200
    
    def patch(self, language_id):
        """Language Update API
        Path - /api/language/<language_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: language_id
              in: path
              type: integer
              required: true
              description: Enter Language ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    lang: 
                        type: string
                    code:
                        type: string
                    message:
                        type: string
        responses:
            200:
                description: Successfully updated language
            404:
                description: Language not found
        """
        found_language = Language.query.filter_by(id=language_id).first()
        if not found_language:
            return get_response("Language not found", None, 404), 404
        
        data = language_update_parse.parse_args()
        lang = data.get('lang', None)
        code = data.get('code', None)
        message = data.get('message', None)

        if lang is not None:
            found_language.lang = lang
        if code is not None:
            found_language.code = code
        if message is not None:
            found_language.message = message
       
        db.session.commit()
        return get_response("Successfully updated language", None, 200), 200

class LanguageListCreateResource(Resource):

    def get(self):
        """Language List API
        Path - /api/language
        Method - GET
        ---
        consumes: application/json
        responses:
            200:
                description: Return Language List
        """
        language_list = Language.query.filter_by().order_by(Language.created_at.desc()).all()
        result_language_list = [Language.to_dict(language) for language in language_list]
        return get_response("Language List", result_language_list, 200), 200
    
    @super_admin_required()
    def post(self):
        """Language Create API
        Path - /api/language
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
                    lang: 
                        type: string
                    code:
                        type: string
                    message:
                        type: string
                required: [lang, code, message]
        responses:
            200:
                description: Return New Language ID
            400:
                description: Lang, Code or Message is Blank
        """
        data = language_create_parse.parse_args()
        lang = data['lang']
        code = data['code']
        message = data['message']
        
        new_language = Language(lang, code, message)
        db.session.add(new_language)
        db.session.commit()
        return get_response("Successfully created language", new_language.id, 200), 200

class LanguageGetResource(Resource):
    
    def get(self, lang, code):
        """Language User Get API
        Path - /api/language/user/<lang>/<code>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - name: lang
              in: path
              type: string
              required: true
              description: Enter Language Lang

            - name: code
              in: path
              type: string
              required: true
              description: Enter Language Code
        responses:
            200:
                description: Return a Language
            404:
                description: Language not found
        """
        language = Language.query.filter_by(lang=lang, code=code).first()
        if not language:
            return get_response("Language not found", None, 404), 404
        
        return get_response("Language successfully found", Language.to_dict(language), 200), 200

api.add_resource(LanguageResource, "/<language_id>")
api.add_resource(LanguageListCreateResource, "/")
api.add_resource(LanguageGetResource, "/user/<lang>/<code>")
