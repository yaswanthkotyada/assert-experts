from flask import Blueprint,request
from sqlmodel import select ,update
from flask_restful import Resource,Api
import logging
from global_varibles import PAGE_LIMIT,OFFICE_NUMBER
from session import get_session
from models import SupportRequest1
from crud import get_user_profile,update_property,get_property_object,send_whatsapp_notifications_to_single_user,send_interest_property_in_english,send_message_template_to_mediator,convert_to_utc
from sqlalchemy.exc import SQLAlchemyError
from webhook_crud import get_area_id_for_area_name,send_message_to_mediator
sp_team_bp=Blueprint("support_team",__name__)
logger=logging.getLogger(__name__)
api=Api(sp_team_bp)

class Help(Resource):
    def post(self):
        try: 
            logger.debug("adding user request for call back")
            data=request.json
            if not data:
                logger.warning("data not provided to add request")
                return {"status":"fail","message":"data not provided to add request"},400
            logger.info(f"call back request data:{data}")
            property_id=data.get("prop_id",None)
            ph_num=data.get("ph_num",None)
            user_name=data.get("user_name","Unknown")
            is_whatsapp_user=data.get("is_whatsapp_user",False)
            intersted_langauge=data.get("langauge","English")
            created_on_date=data.get("date",None)
            if created_on_date:
                utc_time=convert_to_utc(date_str=created_on_date)
                data["created_on"]=utc_time
            with get_session() as session:
                if property_id:
                    prop_obj = get_property_object(property_id, session)
                    if not prop_obj:
                        logger.warning(f"Requested Property {property_id} not existed to update num of leads")
                        return {"status": "fail","message": "Property is not availble"}, 401
                    data["location"]=prop_obj.village
                    data["property_type"]=prop_obj.p_type
                    med_profile_id=prop_obj.cont_user_id
                    if not med_profile_id:
                        logger.debug(f"mediator profile id not exist for property {property_id}")
                        return {"status":"fail","message":f"mediator profile id not exist for property {property_id}"}
                    med_profile_obj=get_user_profile(session=session,user_id=med_profile_id)
                    if not med_profile_obj:
                        logger.debug(f"profile not exist for user id {med_profile_id} to send message")
                        return {"status":"fail","message":f"profile not exists for user id {med_profile_id}"},400
                    is_mediator_is_whatsapp_user=med_profile_obj.is_whatsapp_user
                    num_of_times_notified=prop_obj.num_of_leads
                    mediator_number_1=prop_obj.med_num1
                    mediator_number_2=prop_obj.med_num2
                    if ph_num and is_whatsapp_user !=None:
                        message_to_send=f"Following Customer is interested in your property. Contact him at the earliest.\n*Name*:{user_name}\n*Contact Number*:{ph_num}"
                        if mediator_number_1:
                            seller_number=mediator_number_1
                            if is_mediator_is_whatsapp_user:
                                send_message_to_mediator(recipent_ph_num=mediator_number_1,message_to_send=message_to_send)
                            else:
                                logger.debug("sending template message to mediator")
                                send_message_template_to_mediator(name=user_name,requested_user_ph_num=ph_num,mediator_phone_num=seller_number)
                        elif not mediator_number_1 and mediator_number_2:
                            seller_number=mediator_number_2
                            if is_mediator_is_whatsapp_user:
                                send_message_to_mediator(recipent_ph_num=mediator_number_2,message_to_send=message_to_send)
                            else:
                                send_message_template_to_mediator(name=user_name,ph_num=ph_num,mediator_phone_num=seller_number)
                        else:
                            seller_number=OFFICE_NUMBER
                        logger.debug(f"seller number:{seller_number}")
                        selected_area=prop_obj.village
                        if not selected_area:
                            logger.debug("village not exist for intersted property")
                            return {"status":"fail"}
                        area_obj=get_area_id_for_area_name(area_name=selected_area,session=session)
                        if not area_obj:
                            logger.critical(f"area_obj is not exist for selected area {selected_area} to sent intrested property")
                            return {"status":"fail"} 
                        area_id=area_obj.id
                        logger.debug(f"area_id:{area_id}")
                        user_params={"ph_num":[{"ph_num":ph_num,"langauge":intersted_langauge}],"area_id":area_id}
                        if is_whatsapp_user:
                            send_whatsapp_notifications_to_single_user(prop_obj=prop_obj,params=user_params,seller_number=seller_number,interest=True)
                        else:
                            parameters_in_eng=send_whatsapp_notifications_to_single_user(prop_obj=prop_obj,params=user_params,seller_number=seller_number,get_params=True)
                            params_in_english=[
                            {"type":"text","text":parameters_in_eng["location_in_eng"]},
                            {"type":"text","text":parameters_in_eng["price_in_eng"]},
                            {"type":"text","text":f"*Seller Contact*:{seller_number}"}
                            ]
                            logger.debug(f"params:{params_in_english}")
                            send_interest_property_in_english(property_id=property_id,params_in_english=params_in_english,phone_num=ph_num)
                        
                    if not num_of_times_notified:
                        num_of_times_notified=0
                    num_of_times_notified+=1
                    data_to_update={
                        "num_of_leads":num_of_times_notified
                    }
                    update_property(property_id=property_id, data_to_update=data_to_update,session=session)
                    logger.debug("property updated successfuly")
                query=SupportRequest1(**data)
                session.add(query)
                session.commit()
                logger.info(f"Call requested successfully")
            return {"status":"success","message":"Call requested successfully"},200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while requesting call: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while requesting call: {e}")
            return {"status":"fail","message":"Internall Error"},500

    def get(self):
        try:
            logger.debug("getting all user queries")
            data=request.args.to_dict()
            if not data:
                logger.warning("data not provided to get requests")
                return {"status":"fail","message":"data not provided to get request"},400
            logger.info(f"data to get call back requests:{data}")
            offset=data.get("offset",0)
            req_user_id=data.get("req_user_id",None)
            if not req_user_id:
                logger.warning("required params to get support requests not provided")
                return {"status":"fail","message":"plese provide requsted user id"},400
            with get_session() as session:
                req_user_obj=get_user_profile(user_id=req_user_id,session=session)
                if not req_user_obj:
                    logger.warning(f"user {req_user_id} not exists to get requstes from users")
                    return {"status":"fail","message":"Un Authorized"},404
                if req_user_obj.role not in ["staff","admin"]:
                    logger.warning(f"user {req_user_obj} requested to get support requsets although he was not a admin and staff")
                    return {"status":"fail","message":"Un Authorized"},404
                query=select(SupportRequest1).offset(offset).limit(PAGE_LIMIT)
                req_objs=session.execute(query).scalars().all()
                res_data=[]
                for obj in req_objs:
                    data={
                        "id":obj.id,
                        "name":obj.user_name,
                        "phone_number":obj.ph_num,
                        "property_id":obj.prop_id,
                        "query":obj.req_query,
                        "requsted_on":str(obj.created_on),
                        "s_comments":obj.s_comments,
                        "status":obj.status
                    }
                    res_data.append(data)
                logger.info(f"call requests;{res_data}")
            return {"status":"success","data":res_data},201
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error getting requsted calls: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error getting requsted calls: {e}")
            return {"status":"fail","message":"Internall Error"},500

    def put(self):
        try:
            logger.debug("updating the query of user")
            data=request.json
            logger.debug(f"data to update call request:{data}")
            id=data.get("id",None)
            if not id :
                logger.warning("call id not provided")
                return {"status":"fail","message":"Plese provide id"},400
            data_to_update={}
            for key,value in data.items():
                if hasattr(SupportRequest1,key):
                    data_to_update[key]=value
            logger.info(f"data to update:{data_to_update}")
            with get_session() as session:
                query=update(SupportRequest1).where(SupportRequest1.id==id).values(data_to_update)
                session.execute(query)
                session.commit()
                logger.info("call request Data updated successfully")
            return {"status":"success","message":"data updated successfully","updated_data":data_to_update},200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error updating requsted calls: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error updating requsted calls: {e}")
            return {"status":"fail","message":"Internall Error"},500
api.add_resource(Help,'/help')




