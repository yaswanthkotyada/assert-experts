from datetime import datetime, timezone
from flask import request, Blueprint, jsonify
from flask_restful import Resource, Api
from sqlalchemy.exc import SQLAlchemyError
import logging
from session import get_session
from crud import get_user_profile, get_property_object
price_hist_bp = Blueprint("price_history", __name__)
logger=logging.getLogger(__name__)

api = Api(price_hist_bp)


class get_price_history(Resource):
    def get(self):
        try:
            logger.debug("getting price history")
            data = request.args.to_dict()
            if not data:
                logger.warning("data not provided to get property price history")
            logger.info(f"price history parameters Data:{data}")
            req_user_id = data.get('req_user_id', None)
            # user_id = data.get('user_id', None)
            property_id = data.get("p_id", None)
            if not req_user_id  or not property_id:
                logger.warning("required params not provided for getting price history")
                return {"status":"fail","message":"Please provide user_id , request_id and property_id"}, 400
            with get_session() as session:
                is_admin=False
                req_user_obj = get_user_profile(req_user_id, session)
                if not req_user_obj:
                    logger.warning(f"requested user {req_user_id} for property price history not exists")
                    return {"status":"fail","message":'Unauthorized Access'}, 401
                if req_user_obj.role == 'admin':
                    is_admin=True
                if not is_admin:
                    plan_active=False
                    current_date=datetime.now(timezone.utc)
                    for payment_obj in req_user_obj.payments:
                        plan_active_till=payment_obj.to_date
                        if payment_obj.to_date and current_date<plan_active_till:
                            plan_active=True
                            break
                    if plan_active==False:
                        logger.warning(f"Not a active user requsted get property price history of {property_id}")
                        return {"status":"fail","message":"your plan is not active"}
                prop_obj = get_property_object(property_id, session)
                if not prop_obj:
                    logger.warning("requested property is not existed")
                    return {"status":"fail","message":"Un Authorized access"}, 401
                property_price_history = []
                for price_hist_obj in prop_obj.price_history:
                    property_price_history.append(
                        {
                            "old_price":price_hist_obj.old_price,
                            "updated_on":str(price_hist_obj.updated_on)
                        }
                    )
                logger.info(f"price hist :{property_price_history}")
                return jsonify({"status": 'success', "profile": (property_price_history)})
        except SQLAlchemyError as se:
            logger.error(f"sqlalchemy error occured while getiing price history of {property_id}:{se}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"exception occured while getting price history {property_id}:{e}")
            return {"status":"fail","message": f"Internall Error"}, 500
        

api.add_resource(get_price_history, '/price_hist')
