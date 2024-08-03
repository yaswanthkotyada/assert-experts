from flask import Flask ,Blueprint,request
from flask_restful import Resource,Api
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select,and_,desc
from models import Property,SupportRequest1
from session import get_session
from crud import get_user_profile,convert_to_utc
search_interested_users_bp=Blueprint("search_interested_users",__name__)
logger=logging.getLogger(__name__)
api=Api(search_interested_users_bp)

class Search_Interested_Users(Resource):
    def post(self):
        try:
            logger.debug("processing for intersted users")
            data=request.json
            if not data:
                logger.debug("data not provided to search interested users")
                return {"status":"fail","message":"please provide data to search users"}
            logger.info(f"data to search users:{data}")
            req_by=data.get("req_by",None)
            from_date=data.get("from_date",None)
            if not req_by:
                logger.warning("Requested user id not provided to search the users")
                return {"status":"fail","message":"requsted user id not provided"}
            if from_date:
                from_date=convert_to_utc(date_str=from_date)
            with get_session() as session:
                req_user_obj = get_user_profile(user_id=req_by,session=session)
                if not req_user_obj or req_user_obj.role not in ['admin' ,'staff']:
                    logger.warning(f"Requested user {req_by} is not a admin or not a staff to search the interested users")
                    return {"status":"fail","message":"Un Authorized access"},404
                user_columns = [1 == 1]
                for key, value in data["body"].items():
                    if hasattr(SupportRequest1, key):
                        user_columns.append(getattr(SupportRequest1, key) == value)
                logger.debug(f"user_columns:{user_columns}")
                if from_date:                    
                    users_query = select(SupportRequest1).where(and_(*user_columns),SupportRequest1.created_on>=from_date).order_by(desc(SupportRequest1.created_on))
                else:
                    users_query = select(SupportRequest1).where(and_(*user_columns)).order_by(desc(SupportRequest1.created_on))
                user_objs=session.execute(users_query).scalars().all()
                users_data=[]
                logger.debug(f"user_objs:{user_objs}")
                if user_objs:
                    for user_obj in user_objs:
                        requested_property=user_obj.req_property
                        property_id=None
                        if requested_property:
                            property_id=requested_property.p_id
                        details={
                            "id":user_obj.id,
                            "user_name":user_obj.user_name,
                            "ph_num":user_obj.ph_num,
                            "email":user_obj.email,
                            "req_query":user_obj.req_query,
                            "status":user_obj.status,
                            "location":user_obj.location,
                            "property_id":property_id,
                            "property_type":user_obj.property_type,
                            "s_comments":user_obj.s_comments,
                            "created_on":str(user_obj.created_on)
                        }
                        users_data.append(details)
                return {"status":"success","interested_users":users_data}
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while Searching for interested users: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while Searching for interested users: {e}")
            return {"status":"fail","message":"Internall Error"},500
        
api.add_resource(Search_Interested_Users,'/search_interested_users')