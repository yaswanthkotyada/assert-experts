from flask import request,Blueprint
from flask_restful import Api,Resource
from datetime import datetime
from models import Payment
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from session import get_session
from crud import get_user_profile,get_start_end_dates,create_a_order,generate_order_id,update_user_profile_for_whatsapp_users,update_pmt_obj,get_pmt_obj,date_to_datetime_obj
import logging
from global_varibles import PLAN_FEES

subscrption_plan_bp=Blueprint("subscrption_plan",__name__)
logger=logging.getLogger(__name__)
api=Api(subscrption_plan_bp)

class Subscription(Resource):
    def post(self):
        try:
            logger.debug("creating a oreder")
            data=request.json
            if not data:
                logger.debug("data not provided to create a order")
                return {"status":"fail","message":"plese provide data"},400
            logger.info(f"data to create a order:{data}")
            user_id=data.get("user_id",None)
            req_user_id=data.get("req_user_id",None)
            plan_type=data.get("subscription_plan_type",None)
            pmt_status=data.get("Payment_status","unpaid")
            payment_date=data.get("payment_date",None)
            pmt_gateway=data.get("payment_gateway",None)
            comments=data.get("comments",None)
            transaction_id=data.get("transaction_id",None)
            if not (user_id and req_user_id and plan_type):
                logger.debug("required parmas area not provided to create a oreder")
                return {"status":"fail","message":"plese provide user_id , req_user_id , plan_type to create a order"},400
            if plan_type not  in PLAN_FEES:
                logger.debug(f"{plan_type} is not a valid paln")
                return {"status":"fail","message":"plese select a valid plan"},400
            with get_session()  as session:
                req_user_obj=get_user_profile(user_id=req_user_id,session=session)
                if not req_user_obj:
                    logger.warning(f"requsted user {req_user_id} tried to crete a oreder although they didnot have a profile")
                    return {"status":"fail","message":"Un Authoruzied"},404
                if req_user_obj.role not in ["staff","admin"]:
                    logger.warning(f"{req_user_id} tried to create a oreder")
                    return {"status":"fail","message":"Un Authoruzied"},404
                pmt_period=PLAN_FEES[plan_type]["period_in_months"]
                num_of_notifications=PLAN_FEES[plan_type]["number_of_notifications"]
                plan_value=PLAN_FEES[plan_type]["value"]
                order_id=generate_order_id()
                plan_starts_at,plan_ends_at=get_start_end_dates(pmt_period)
                start_date_time_obj=datetime.strptime(plan_starts_at, "%d-%m-%y")
                end_date_time_obj=datetime.strptime(plan_ends_at, "%d-%m-%y")
                data_to_add={
                    "u_id":user_id,
                    "subscription_plan_type":plan_type,
                    "from_date":start_date_time_obj,
                    "to_date":end_date_time_obj,
                    "Payment_status":pmt_status,
                    "price":plan_value,
                    "order_id":order_id,
                    "payment_gateway":pmt_gateway,
                    "comments":comments,
                    "transaction_id":transaction_id}
                if payment_date:
                    payment_date=date_to_datetime_obj(payment_date)
                    present_date=datetime.now()
                    if payment_date>present_date:
                        logger.debug(f"user {req_user_id} trying to create oreder for future")
                        return {"status":"fail","message":"creatation of order for future is not accepted"},400
                    data_to_add["payment_date"]=payment_date
                # if payment_date:
                #     try:
                #         payment_date = datetime.strptime(payment_date, "%d-%m-%Y")
                #         present_date=datetime.now()
                #         if payment_date>present_date:
                #             logger.debug(f"user {req_user_id} trying to create oreder for future")
                #             return {"status":"fail","message":"cretation of order for future is not accepted"},400
                #         data_to_add["payment_date"]=payment_date
                #     except ValueError as ve:
                #         logger.error(f"Error converting date: {ve}")
                #         raise ve
                logger.debug(f"data for the creation of order:{data_to_add}")
                payment_details=create_a_order(session=session,data_to_add=data_to_add)
                logger.debug(f"oreder created successfully")
                if pmt_status=="paid":
                    logger.debug("updating the number of notifications for the user")
                    user_obj=get_user_profile(user_id=user_id,session=session)
                    if not user_obj:
                        logger.debug(f"user {user_id} not exists to create a order")
                        return {"status":"fail","message":"user not exists"},400
                    present_active_notifications=user_obj.active_notifications
                    data_to_update={
                        "active_notifications":present_active_notifications+num_of_notifications
                    }
                    update_user_profile_for_whatsapp_users(session=session,user_id=user_id,data_to_update=data_to_update)
                    payment_details["active_notifications"]=user_obj.active_notifications
                logger.info(f"order details:{payment_details}")
                return {"status":"success","message":"oreder created successfully","payments":payment_details} ,201
        except ValueError as ve:
            logger.warning(f"only date time with '%y-%m-%d' these format accepted:{ve}")
            return {"status":"fail","message":"only date time with '%y-%m-%d' these format accepted"},400
        except IntegrityError as se:
            logger.error(f"Integrity error while creating the order: {se.orig}")
            return {"status": "fail", "message": "oredr alredy exists"}, 400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while creating the order: {e}")
            return {"status": "fail", "message": "Server Error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error while creating the order: {e}")
        return {"status": "fail", "message": "Internal Error"}, 500
     
    def put(self):
        try:
            logger.debug("updating the status of a order")
            data=request.json
            if not data:
                logger.debug("data not provided to create the oreder")
                return {"status":"fail","message":"plese provide data"},400
            logger.info(f"data to update:{data}")
            pmt_id=data.get("payment_id",None)
            user_id=data.get("user_id",None)
            req_user_id=data.get("req_user_id",None)
            payment_date=data.get("payment_date",None)
            active_notifications=data.get("active_notifications",None)
            plan_type=data.get("subscription_plan_type",None)
            from_date=data.get("from_date",None)
            to_date=data.get("to_date",None)
            if not (user_id and req_user_id and pmt_id  ):
                logger.debug("required parmas area not provided to update a oreder")
                return {"status":"fail","message":"plese provide user_id , req_user_id"},400
            with get_session()  as session:
                req_user_obj=get_user_profile(user_id=req_user_id,session=session)
                user_obj=get_user_profile(user_id=user_id,session=session)
                if not req_user_obj :
                    logger.warning(f"requsted user {req_user_id} tried to crete a oreder although they didnot have a profile")
                    return {"status":"fail","message":"Un Authoruzied"},404
                if not user_obj :
                    logger.warning(f"user {user_id} does not exists to update the order {pmt_id}")
                    return {"status":"fail","message":"Un Authoruzied"},404
                if req_user_obj.role not in ["staff","admin"]:
                    logger.warning(f"{req_user_id} tried to create a oreder")
                    return {"status":"fail","message":"Un Authoruzied"},404
                pmt_obj=get_pmt_obj(session=session,pmt_id=pmt_id)
                if not pmt_obj:
                    logger.critical(f"order not exists with payment id {pmt_id}")
                    return {"status":"fail","message":f"order not exist with {pmt_id}"},400
                if pmt_obj.u_id !=user_id:
                    logger.warning(f"order {pmt_id} not belongs to {user_id}")
                    return {"status":"fail","message":"Un Authorized"},404
                if plan_type not  in PLAN_FEES:
                    logger.debug(f"{plan_type} is not a valid paln")
                    return {"status":"fail","message":"plese select a valid plan"},400
                old_pmt_status=pmt_obj.Payment_status
                plan_active_from=pmt_obj.from_date
                logger.debug(f"old payment status:{old_pmt_status}")
                if payment_date:
                    payment_date=date_to_datetime_obj(payment_date)
                    data["payment_date"]=payment_date
                if to_date and from_date:
                    from_date=date_to_datetime_obj(from_date)
                    to_date=date_to_datetime_obj(to_date)
                    present_date=datetime.now()
                    if from_date>present_date:
                        logger.debug(f"user {req_user_id} trying to create oreder for future")
                        return {"status":"fail","message":"cretation of order for future is not accepted"},400
                    if from_date>to_date:
                        logger.warning(f"not valid time period")
                        return {"status":"fail","message":"not a valid time period"},400
                    data["from_date"]=from_date
                    data["to_date"]=to_date
                elif not from_date and to_date and plan_active_from:
                    to_date=date_to_datetime_obj(to_date)
                    if plan_active_from>to_date:
                        logger.warning(f"not valid time period")
                        return {"status":"fail","message":"not a valid time period"},400
                    data["to_date"]=to_date
                data_to_update = {}
                for key, value in data.items():
                    if hasattr(Payment, key):
                        data_to_update[key]=value
                logger.debug(f"data to update:{data_to_update}")
                if len(data_to_update)==0:
                    logger.debug(f"data provided to update the order")
                    return {"status":"fail","message":"plese provide data to update the order"},400
                logger.debug(f"pmt_status old:{old_pmt_status}")
                pmt_id=pmt_obj.id
                logger.debug(f"payment id:{pmt_id}")
                update_pmt_obj(session=session,pmt_id=pmt_id,data_to_update=data_to_update)
                new_status=pmt_obj.Payment_status
                plan_type=pmt_obj.subscription_plan_type
                payment_details={
                        "payment_id":pmt_obj.id,
                        "payment_gateway":pmt_obj.payment_gateway,
                        "price":pmt_obj.price,
                        "order_id":pmt_obj.order_id,
                        "transaction_id":pmt_obj.transaction_id,
                        "payment_date":str(pmt_obj.payment_date),
                        "from_date":str(pmt_obj.from_date),
                        "to_date":str(pmt_obj.to_date),
                        "subscription_plan_type":pmt_obj.subscription_plan_type,
                        "Payment_status":pmt_obj.Payment_status,
                        "comments":pmt_obj.comments
                    }
                if active_notifications:
                    logger.debug("updating the number of notifications for the user which are provided by admin")
                    user_obj=get_user_profile(user_id=user_id,session=session)
                    if not user_obj:
                        logger.debug(f"user {user_id} not exists to create a order")
                        return {"status":"fail","message":"user not exists"},400
                    logger.debug(f"user_obj:{user_obj}")
                    present_active_notifications=user_obj.active_notifications
                    data_to_update_fr_user={
                        "active_notifications":present_active_notifications+active_notifications
                    }
                    update_user_profile_for_whatsapp_users(session=session,user_id=user_id,data_to_update=data_to_update_fr_user)
                    logger.debug("user active notifications updated successfully")
                    payment_details["active_notifications"]=user_obj.active_notifications
                else:
                    if new_status=="paid" and old_pmt_status=="unpaid" and plan_type:
                        logger.debug("updating the number of notifications for the user")
                        user_obj=get_user_profile(user_id=user_id,session=session)
                        if not user_obj:
                            logger.debug(f"user {user_id} not exists to create a order")
                            return {"status":"fail","message":"user not exists"},400
                        num_of_notifications=PLAN_FEES[plan_type]["number_of_notifications"]
                        logger.debug(f"user_obj:{user_obj}")
                        present_active_notifications=user_obj.active_notifications
                        data_to_update_fr_user={
                            "active_notifications":present_active_notifications+num_of_notifications
                        }
                        update_user_profile_for_whatsapp_users(session=session,user_id=user_id,data_to_update=data_to_update_fr_user)
                        logger.debug("user active notifications updated successfully")
                        payment_details["active_notifications"]=user_obj.active_notifications
                logger.debug("payment updated successfully")
                logger.info(f"order details:{payment_details}")
            return {"status":"success","message":f"order updated successfully","payments":payment_details},200
        except ValueError as ve:
            logger.warning("only date time with '%Y-%m-%d %H:%M:%S' these format accepted")
            return {"status":"fail","message":"only date time with '%Y-%m-%d %H:%M:%S' these format accepted"},400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while updating the order: {e}")
            return {"status": "fail", "message": "Server Error"}, 500
        except Exception as e:
            logger.critical(f"unexpected error while updating the order: {e}")
        return {"status": "fail", "message": "Internal Error"}, 500
                
api.add_resource(Subscription,'/plan')