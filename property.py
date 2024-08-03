from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from session import get_session
import logging
from crud import get_user_profile, update_property, get_property_object, add_Propert_Price_History, send_whatsapp_notifications,individual_property_details
from flask_restful import Resource, Api
from models import Property
from datetime import datetime, timezone

property_bp = Blueprint("property", __name__)
logger = logging.getLogger(__name__)

api = Api(property_bp)

class property(Resource):
    def post(self):
        try:
            logger.debug("adding the property")
            data = request.json
            if not data:
                logger.debug("data not provided to add the property")
                return {"status":"fail","message":"plese provide data"},400             
            logger.info(f"Property Data to add:{data}")
            user_id=data.get("cont_user_id",None)
            unit=data.get("unit",None)
            size=data.get("size",None)
            listing_type=data.get("listing_type",None)
            property_type=data.get("p_type",None)
            price=data.get("price",None)
            doc_num=data.get("doc_num",None)
            state=data.get("state",None)
            district=data.get("district",None)
            village=data.get("village",None)
            bhk=data.get("bhk",None)
            if not(user_id and unit and size  and listing_type and property_type and state and district and village):
                logger.debug("required params not provided to add property")
                return {"status":"fail","message":"plese provide (user_id , unit , size  , listing_type , property_type , state , district and village) to add property"},400
            if property_type=="flat" and not bhk:
                logger.debug("bhk not provided to add flat")
                return {"status":"fail","message":"plese provide bhk to add property"},400
            if listing_type=="sell" and not price:
                logger.debug("property price not provided to add property")
                return {"status":"fail","message":"plese provide price to add property"},400
            if listing_type=="buy" and not doc_num:
                logger.debug("property price range not provided to add property")
                return {"status":"fail","message":"plese provide price range to add property"},400
            if listing_type=="buy" and doc_num:
                min_max_values=doc_num.split("-")
                if len(min_max_values)!=2:
                    logger.debug("property price not provided in expected format")
                    return {"status":"fail","message":"plese provide price range 'min-max' format"},400
            with get_session() as session:
                user_obj=get_user_profile(session=session,user_id=user_id)
                if not user_obj:
                    logger.warning(f"User {user_id} attempted to add a property without having an account")
                    return {"status":"fail","message":"Before adding the property, please complete the sign-up process"},400
                if user_obj.status=="inactive":
                    logger.warning(f"user {user_id} attempted to add property with an inactive profile status")
                    return {"status":"fail","message":"Un Authorized"},404
                prop_obj = Property(**data)
                session.add(prop_obj)
                session.commit()
                prop_id = prop_obj.p_id
                user_id = prop_obj.cont_user_id
                logger.debug(f"added property id:{prop_id} of user id:{user_id}")
                property_details=individual_property_details(property_obj=prop_obj,is_admin=False)
                property_details["property"]["req_user_id"]=user_id
                logger.info(f"property {prop_id} added successfully")
                return {
                    "status": "success",
                    "message": "property added successfully",
                    "details": property_details
                }, 201
        except IntegrityError as se:
            logger.error(f"Integrity error while adding property: {se.orig}")
            return {"status": "fail", "message": "property alredy exists"}, 400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while adding property: {e}")
            return {"status": "fail", "message": "Server Error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error while adding property: {e}")
            return {"status": "fail", "message": "Internal Error"}, 500


    def get(self):
        try:
            logger.debug("getting property data")
            data = request.args.to_dict()
            if not data:
                logger.warning("data not provided to get the property details")
                return {"status":"fail","message":"plese provide data"},400 
            logger.info(f"Data to get the property details:{data}")
            req_user_id = data.get('req_user_id', None)
            user_id = data.get('user_id', None)
            property_id = data.get("p_id", None)
            if not req_user_id or not user_id or not property_id:
                logger.warning("required params to get property is not provided")
                return {"status": "fail", "message": "Please provide user_id , request_id and property_id"}, 400
            with get_session() as session:
                is_admin = False
                if user_id != req_user_id:
                    req_user_obj = get_user_profile(req_user_id, session)
                    if req_user_obj is None:
                        logger.warning(f"requseted user {req_user_id} profile is not exists")
                        return {
                            "status": "fail",
                            "message": 'Unauthorized Access'
                        }, 401
                    elif req_user_obj.role not in ['admin', "staff"]:
                        logger.warning(f"unkown person requsted to get property:{property_id}")
                        return {"status": "fail", "message": 'Unauthorized request'}, 401
                    else:
                        is_admin = True
                prop_obj = get_property_object(property_id, session)
                if not prop_obj:
                    logger.warning(f"requested property {property_id} trying to get not existed")
                    return {
                        "status": "fail",
                        "message": "Un Authorized access"
                    }, 401
                logger.debug(f"property details:{prop_obj}")
                if prop_obj.cont_user_id != user_id:
                    logger.warning(f"Trying to acces property that not belongs to {user_id}")
                    return {"status": "fail", "message": "Un Authorized"}, 401
                prop_imgs = []
                for image_objs in prop_obj.all_prop_imgs:
                    if image_objs:
                        prop_imgs.append(image_objs.img_url)
                property=individual_property_details(property_obj=prop_obj,is_admin=is_admin,is_image_ids_required=False)
                logger.info(f"property details of {property_id}:{property}")
                return {
                    "status": 'success',
                    "details": property}, 200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while getting property details: {e}")
            return {"status": "fail", "message": "Server Error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error while getting property details: {e}")
            return {"status": "fail", "message": "Internall Error"}, 500

    def put(self):
        try:
            logger.debug("updating the property")
            data = request.json
            if not data:
                logger.warning("date not provided to update the property")
                return {"status": "fail", "message": "Please provide property data"}, 400
            logger.info(f"Property data to update:{data}")
            req_user_id = data.get('req_user_id', None)
            user_id = data.get('user_id', None)
            property_id = data.get("p_id", None)
            if not req_user_id or not user_id or not property_id:
                logger.warning("req user or user id or property_id not provided to update the data")
                return {
                    "status": "fail",
                    "message": "Please provide user_id , request_id and property_id"
                }, 400
            with get_session() as session:
                is_admin = False
                if user_id != req_user_id:
                    req_user_obj = get_user_profile(req_user_id, session)
                    if not req_user_obj:
                        logger.warning(f"requested user {req_user_id} to update the property is not found")
                        return {
                            "status": "fail",
                            "message": 'Unauthorized Access'
                        }, 401
                    if req_user_obj.role not in ['admin', "staff"]:
                        logger.warning(f"user {req_user_id} requsted to update other property {property_id} details")
                        return {"status": "fail", "message": 'Unauthorized request'}, 401
                    is_admin = True
                prop_obj = get_property_object(property_id, session)
                if not prop_obj:
                    logger.warning(f"Requested Property {property_id} not existed to update")
                    return {"status": "fail","message": "Property is not availble"}, 401
                if prop_obj.cont_user_id != user_id:
                    logger.warning(f"user not belongs to the requsted property {property_id}")
                    return {"status": "fail","message": "Un Authorized"}, 401
                orginall_price=prop_obj.price
                price_to_update=data.get("price",None)
                logger.debug(f"orginall price of the property:{orginall_price} ,requsted price of the property to update:{price_to_update}")
                if price_to_update and not is_admin and orginall_price!=price_to_update:
                    logger.warning(f"user {user_id} trying to update the price")
                    return {"status":"faill","message":"You are not allowed to update the price. Please put your new price in the comment section, we will update it soon."},400
                data_to_update = {}
                for key, value in data.items():
                    if hasattr(Property, key):
                        if not is_admin and key not in ["v_status", "v_comments","price","docFile","notified","num_of_times_notified"]:
                            data_to_update[key] = value
                        elif is_admin:
                            data_to_update[key] = value
                        else:
                            pass
                old_price = orginall_price
                if price_to_update and price_to_update >= 1.05 * old_price:
                    add_Propert_Price_History(session=session, property_id=property_id, old_price=old_price)
                    logger.debug("past price added successfuly")
                data_to_update["p_updated_on"] = datetime.now(timezone.utc)
                if not is_admin:
                    data_to_update["updated_by"] = user_id
                    data_to_update["v_status"]=False
                else:
                    data_to_update["updated_by"] = req_user_id
                update_property(property_id=property_id, data_to_update=data_to_update,session=session)
                property_notified_status=prop_obj.notified
                logger.debug(f"property notified status:{property_notified_status}")
                if prop_obj.status == "active" and prop_obj.v_status==True and  property_notified_status==False:
                    logger.debug(f"sending whatsapp notifications for property {property_id}")
                    res_obj = send_whatsapp_notifications(prop_obj=prop_obj, session=session)
                    action=res_obj.get("action")
                    totall_users=res_obj.get("total_users")
                    if action:
                        num_of_times_notified = prop_obj.num_of_times_notified
                        if not num_of_times_notified:
                            num_of_times_notified=0
                        num_of_times_notified += totall_users
                        data_to_update={"num_of_times_notified":num_of_times_notified,"notified":True}
                        update_property(property_id=property_id, data_to_update=data_to_update,session=session)
                property_details=individual_property_details(property_obj=prop_obj,is_admin=False)
                property_details["property"]["req_user_id"]=req_user_id
                logger.info("property updated successfully")
                return {
                    "status": "success", "message": "Property updated successfully",
                    "details":property_details
                    }
        except ValueError as ve:
            logger.error(f"value error while updating the property:{ve}")
            return {"status": "fail", "message": str(ve)}, 400
        except IntegrityError as se:
            logger.error(f"Integrity error while updating the property: {se.orig}")
            return {"status": "fail", "message": se}, 400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while updating the property: {e}")
            return {"status": "fail", "message": "Server Error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error while updating the property: {e}")
            return {"status": "fail", "message": "Internall Error"}, 500


api.add_resource(property, '/property')
