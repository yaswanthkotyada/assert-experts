from flask import Blueprint, request
from flask_restful import Api, Resource
from sqlalchemy import func
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import and_, select
from sqlmodel.sql.expression import desc
from global_varibles import PAGE_LIMIT
from crud import get_user_profile
from models import User
from session import get_session
page_limit=PAGE_LIMIT
user_search_bp = Blueprint("user_search", __name__)
logger=logging.getLogger(__name__)
api = Api(user_search_bp)

class Search_Users(Resource):
    def post(self):
        try:
            logger.debug("searching for users")
            data = request.json
            if not data:
                logger.info("data not provided for searching")
                return {"status": "fail", "message": "data not provided"}, 400
            logger.debug(f"data to search users:{data}")
            req_by = data.get("req_user_id", None)
            offset = data.get("offset", 0)
            with get_session() as session:
                if not req_by:
                    logger.warning("Requested user id not provided to search the users")
                    return {"status":"fail","message":"requsted user id not provided"}
                user_obj = get_user_profile(user_id=req_by,session=session)
                if not user_obj or user_obj.role not in ['admin' ,'staff']:
                    logger.warning(f"Requested user {req_by} is not a admin or not a staff to search the users")
                    return {"status":"fail","message":"Un Authorized access"},404
                user_columns = [1 == 1]
                col={}
                for key, value in data.items():
                    if hasattr(User, key) and value!='':
                        user_columns.append(getattr(User, key) == value)
                        col[key]=value
                logger.debug(f"col:{col}")
                tot_users_count = 0
                user_query = select(User).where(and_(*user_columns)).limit(0)
                if len(user_columns)>1:
                    if offset == 0:
                        tot_users_count = session.execute(select(func.count(User.id)).filter(and_(*user_columns))).scalar()
                    user_query = select(User).where(and_(*user_columns)).order_by(desc(User.created_on)).offset(offset).limit(page_limit)
                user_objs = session.execute(user_query).scalars().all()
                logger.info("Fetching all users")
                users = self.process_users(user_objs=user_objs)
                logger.info(f"tot_users_count:{tot_users_count}")
                return {
                    "status": "success",
                    "users": users,
                    "total_users": tot_users_count
                }
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while Searching for users: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while Searching for users: {e}")
            return {"status":"fail","message":"Internall Error"},500

    def process_users(self, user_objs):
        users_details=[]
        for user_obj in user_objs:
            user_details={
            "id": user_obj.id,
            "name": user_obj.name,
            "ph_num_1": user_obj.ph_num_1,
            "ph_num_2": user_obj.ph_num_2,
            "profession": user_obj.profession,
            "address": user_obj.address,
            "email": user_obj.email,
            "role": user_obj.role,
            "status":user_obj.status,
            "requirements": user_obj.requirements,
            "comments":user_obj.comments,
            "created_on":str(user_obj.created_on),
            "updated_on":str(user_obj.updated_on),
            "updated_by":user_obj.updated_by
            }
            users_details.append(user_details)
        return users_details


api.add_resource(Search_Users, '/search_users')
