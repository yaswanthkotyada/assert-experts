from flask import Blueprint, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_restful import Api, Resource
from models import User
import logging
from session import get_session
from crud import get_user_profile, update_profile,update_user_profile_for_whatsapp_users,individual_property_details
from user_interested_areas_crud import get_user_obj_with_ph_nums,change_user_id_in_areas,delete_user
from datetime import datetime, timezone

user_bp = Blueprint('user', __name__)
logger=logging.getLogger(__name__)
api = Api(user_bp)
    
class user_profile(Resource):
    def post(self):
        try:
            logger.debug("adding new user")
            data = request.json
            if not data:
                logger.warning("data not provided to add the user")
                return {"status":"fail","message":"plese provide data"},400
            logger.info(f"User data to add:{data}")
            user_id=data.get("id",None)
            ph_num_1=data.get("ph_num_1",None)
            ph_num_2=data.get("ph_num_2",None)
            if not user_id:
                logger.warning("user id not provided to add user")
                return {"status":"fail","message":"plese provide user id"},400
            with get_session() as session:
                new_user = User(**data)
                session.add(new_user)
                session.commit()
                logger.info(f"User {new_user.id} added successfully")
                ph_num_1=str(ph_num_1)
                ph_num_2=str(ph_num_2)
                duplicate_user_obj=get_user_obj_with_ph_nums(session=session,ph_num_1=ph_num_1,ph_num_2=ph_num_2)
                if duplicate_user_obj:
                    logger.debug("deleting alredy registered areas")
                    duplicate_user_id=duplicate_user_obj.id
                    data_to_update={}
                    if duplicate_user_id !=ph_num_1:
                        logger.debug("swaping user phone number")
                        data_to_update["ph_num_1"]=ph_num_2
                        data_to_update["ph_num_2"]=ph_num_1
                    change_user_id_in_areas(session=session,ph_num=duplicate_user_id,user_id=user_id)
                    delete_user(session=session,user_id=duplicate_user_id)
                    data_to_update["is_whatsapp_user"]=True
                    update_user_profile_for_whatsapp_users(session=session, user_id=user_id, data_to_update=data_to_update)
                return {
                    "status": "success",
                    "message": "User added successfully",
                    "data": data}, 201
        except IntegrityError as se:
            logger.error(f"Integrity error while adding user:{se.orig}")
            return {"status":"fail","message": f"user alredy exists"}, 400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while adding user: {e}")
            return {"status":"fail","message": "Server Error"}, 400
        except Exception as e:
            logger.critical(f"unexpected error while adding user:{e}")
            return {"status":"fail","message": "Internall Error"}, 500

    def get(self):
        try:
            logger.debug("getting user details")
            data = request.args.to_dict()
            if not data:
                logger.warning("data not provided to get the user details")
                return {"status":"fail","message":"plese provide data"},400
            logger.info(f"Data to get user details:{data}")
            req_user_id = data.get('req_user_id', None)
            user_id = data.get('user_id', None)
            if not req_user_id or not user_id:
                logger.warning("required params not provided to get user details")
                return {
                    "status": "fail",
                    "message": "Please provide user_id and request_id"
                }, 400
            with get_session() as session:
                req_user_obj = get_user_profile(req_user_id, session)
                logger.debug(f"requsetd user to get the user profile:{req_user_obj}")
                if req_user_obj is None:
                    logger.warning(f"requseted user {req_user_id} profile is not exists")
                    return {
                        "status": "fail",
                        "message": 'Unauthorized Access'
                    }, 401
                is_admin = False
                if user_id != req_user_id:
                    if req_user_obj.role in ['admin', 'staff']:
                        is_admin = True
                user_obj = get_user_profile(user_id, session)
                if not user_obj:
                    logger.warning(f"user {user_id} profile is not availble to get their details")
                    return {
                        "status": "fail",
                        "message": "Un Authorized access"
                    }, 401
                payments=[]
                payment_objs=user_obj.payments
                for payment_obj in payment_objs:
                    paymenty_data={
                        "payment_id":payment_obj.id,
                        "payment_gateway":payment_obj.payment_gateway,
                        "price":payment_obj.price,
                        "order_id":payment_obj.order_id,
                        "transaction_id":payment_obj.transaction_id,
                        "payment_date":str(payment_obj.payment_date),
                        "from_date":str(payment_obj.from_date),
                        "to_date":str(payment_obj.to_date),
                        "subscription_plan_type":payment_obj.subscription_plan_type,
                        "Payment_status":payment_obj.Payment_status,
                        "comments":payment_obj.comments,
                        "active_notifications":user_obj.active_notifications,
                        "is_whatsapp_user":user_obj.is_whatsapp_user
                    }
                    payments.append(paymenty_data)
                registered_areas = [area_obj.name for area_obj in user_obj.areas]
                properties = []
                for prop_obj in user_obj.all_properties[::-1]:
                    property_images = []
                    for image_objs in prop_obj.all_prop_imgs:
                        if image_objs:
                            property_images.append(image_objs.img_url)
                    developments=[]
                    if  prop_obj.developments: 
                        developments=prop_obj.developments.split(',')
                    if len(developments)==0:
                        developments=""
                    property=individual_property_details(property_obj=prop_obj,is_admin=is_admin,is_image_ids_required=False)
                    property=property["property"]
                    properties.append(property)
                phone_num_1= user_obj.ph_num_1
                phone_num_2= user_obj.ph_num_2
                if phone_num_1 and len(str(phone_num_1))==12:
                    phone_num_1=str(phone_num_1)
                    phone_num_1=phone_num_1[2:]
                    phone_num_1=int(phone_num_1)
                if phone_num_2 and len(str(phone_num_2))==12:
                    phone_num_2=str(phone_num_2)
                    phone_num_2=phone_num_2[2:]
                    phone_num_2=int(phone_num_2)
                profile = {
                    "user_id":user_obj.id,
                    "name": user_obj.name,
                    "phone_num_1": phone_num_1,
                    "phone_num_2": phone_num_2,
                    "profession": user_obj.profession,
                    "address": user_obj.address,
                    "comments": user_obj.comments,
                    "email": user_obj.email,
                    "role": user_obj.role,
                    "status":user_obj.status,
                    "langauge":user_obj.prefered_langauge,
                    "active_notifications":user_obj.active_notifications,
                    "requirements": user_obj.requirements,
                    "is_whatsapp_user":user_obj.is_whatsapp_user,
                    "number_of_times_notified":user_obj.num_of_notifications_notified
                }
                logger.info(f"user profile {profile},user properties:{properties},user registered areas:{registered_areas} ,payments:{payments}")
                return {'status': 'success', "profile": profile,"properties":properties,"interested_areas":registered_areas,"payments":payments}, 200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while getting user: {e}")
            return {"status":"fail","message": "Server Error"}, 400
        except Exception as e:
            logger.critical(f"unexpected error while getting user:{e}")
            return {"status":"fail","message": "Internall Error"}, 500


    def put(self):
        try:
            logger.debug("Updating the user profile")
            data = request.json
            if not data:
                logger.warning("data is not provided to update the user")
                return {
                    "status": "fail",
                    "message": "Please provide data"
                }, 400
            logger.info(f"data to update the user profile:{data}")
            req_user_id = data.get("req_user_id", None)
            user_id = data.get("user_id", None)
            if not req_user_id or not user_id:
                logger.warning("required params not provided to update user details")
                return {
                    'status': 'fail',
                    "message": "Plese provide user_id and requested user_id"
                }, 400
            with get_session() as session:
                req_user_obj = get_user_profile(req_user_id, session)
                logger.debug(f"requsetd user to update the user profile:{req_user_obj}")
                if not req_user_obj:
                    logger.warning(f"requseted user {req_user_id} profile is not exists")
                    return {
                        'status': 'fail',
                        "message": "Un Authorized Access"
                    }, 401
                is_admin = False
                req_user_role = req_user_obj.role
                if req_user_id != user_id:
                    if req_user_role not in ['admin', 'staff']:
                        logger.warning(f"Requested user to update the user profile {user_id} was not a admin or not a staff")
                        return {
                            'status': 'fail',
                            "message": "Un Authorized"
                        }, 401
                    is_admin = True
                user_obj = get_user_profile(user_id, session)
                if not user_obj:
                    logger.warning(f"user {user_id} profile is not availble to update their details")
                    return {
                        'status': 'fail',
                        "message": "Un Authorized Access"
                    }, 401
                data_to_update = {}
                for key, value in data.items():
                    if hasattr(User, key) :
                        if not is_admin and key not in ['role', 'comments','active_notifications','num_of_notifications_notified','status']:
                            data_to_update[key] = value
                        elif is_admin:
                            if req_user_role =="staff" and key not in ["role"]:
                                data_to_update[key] = value
                            elif req_user_role=="admin":
                                data_to_update[key] = value
                            else:
                                pass
                         
                data_to_update["updated_on"] = datetime.now(timezone.utc)
                if not is_admin:
                    data_to_update["updated_by"] = user_id
                else:
                    data_to_update["updated_by"] = req_user_id
                logger.info(f"data_to_update:{data_to_update}")
                update_profile(user_id, data_to_update, session)
                return {'status': 'success', "data": {
                                            "user_id":user_obj.id,
                                            "name": user_obj.name,
                                            "phone_num_1": user_obj.ph_num_1,
                                            "phone_num_2": user_obj.ph_num_2,
                                            "profession": user_obj.profession,
                                            "address": user_obj.address,
                                            "comments": user_obj.comments,
                                            "email": user_obj.email,
                                            "role": user_obj.role,
                                            "requirements": user_obj.requirements}},201
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while updating user: {e}")
            return {"status":"fail","message": "Server Error"}, 400
        except Exception as e:
            logger.critical(f"unexpected error while updating user:{e}")
            return {"status":"fail","message": "Internall Error"}, 500


api.add_resource(user_profile, '/user')
