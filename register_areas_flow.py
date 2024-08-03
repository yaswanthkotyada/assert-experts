
import json
import logging
from flask import Blueprint, request, Response
from flask_restful import Api, Resource
from sqlalchemy.exc import SQLAlchemyError
from web_nrml_flow_operations import PayloadProcessor
from encrypt_decrypt_response import PROCESS_WHATSAPP_DATA

register_areas_flow_bp = Blueprint("register_areas_flow", __name__)
logger=logging.getLogger(__name__)

api = Api(register_areas_flow_bp)

processor = PayloadProcessor()
data_processor=PROCESS_WHATSAPP_DATA()
class Register_Areas_Webhook(Resource):
    def post(self):
        try:
            body = json.loads(request.data)
            logger.info(f"encrypted data:{body}")
            if body:
                signature = request.headers.get('X-Hub-Signature-256')
                if not signature or not data_processor.validate_signature(request.data, signature):
                    logger.debug("Signature validation failed")
                    return {"status":"fail","message":"Signature validation failed"}, 403
                encrypted_flow_data_b64 = body.get('encrypted_flow_data')
                encrypted_aes_key_b64 = body.get('encrypted_aes_key')
                initial_vector_b64 = body.get('initial_vector')
                decrypted_data, aes_key, iv = data_processor.decrypt_request(
                    encrypted_flow_data_b64, encrypted_aes_key_b64, initial_vector_b64)
                logger.info(f"decrypted_data:{decrypted_data}")
                flow_token=decrypted_data.get("flow_token",None)
                action=decrypted_data.get("action",None)
                version = decrypted_data.get("version")
                logger.debug(f"flow_token:{flow_token}")
                logger.debug(f"action:{action}")
                logger.debug(f"version:{version}")
                if not flow_token and action=="ping":
                    response_data={"version": version,"data": {"status": "active"}}
                if flow_token:
                    response_data = processor.process_payload(payload=decrypted_data)
                logger.info(f"response data:{response_data}")
                encrypted_response = data_processor.encrypt_response(response_data, aes_key, iv)
                return Response(encrypted_response, content_type='text/plain')

        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error in whatsaap flow: {e}")
            return {"status":"fail","message": "Server Error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error in whatsaap flow:{e}")
            return {"status":"fail","message": "Internall Error"}, 500
    

api.add_resource(Register_Areas_Webhook, '/register_intersted_areas')