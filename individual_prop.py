from flask import Blueprint, request
import logging
from flask_restful import Api, Resource
from session import get_session
from crud import get_property_object,get_user_profile,get_property_details
from sqlalchemy.exc import SQLAlchemyError

individual_prop_bp = Blueprint("individual_prop", __name__)
logger=logging.getLogger(__name__)
api = Api(individual_prop_bp)


class Individual_Property(Resource):    
    def get(self):
        try:
            logger.debug("getting individual property")
            data = request.args.to_dict()
            if not data:
                logger.warning("data not provided to get individual property details")
            logger.info(f"individual property parameters:{data}")
            prop_id = data.get("prop_id", None)
            req_by=data.get("req_by",None)
            if not prop_id:
                logger.warning("property id not provide to see entire property details")
                return {"status":"fail","message": "Please Provide Property_id"}, 400
            with get_session() as session:
                is_admin=False
                if req_by:
                    user_obj=get_user_profile(user_id=req_by,session=session)
                    if user_obj and user_obj.role=='admin' or user_obj.role=='staff':
                        is_admin=True
                prop_object_req = get_property_object(prop_id, session)
                logger.debug(f"requested_property object:{prop_object_req}")
                if not prop_object_req:
                    logging.warning("requested property is not availble")
                    return {"status":"fail","message":f"requested property {prop_id} not exist"},404
                property_details=get_property_details(prop_object_req=prop_object_req,session=session,is_admin=is_admin)                    
                logger.info(f"property_datils:{property_details}")      
                return property_details,200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while fetching individual property: {e}")
            return {"status":"fail","message":"Server error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error while fetching individual property :{e}")
            return {"status":"fail","message": "Internall server error"}, 500



api.add_resource(Individual_Property, '/property_ind')
