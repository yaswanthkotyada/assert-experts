from flask import Blueprint, request
from flask_restful import Api, Resource
from sqlalchemy import func
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import and_, select
from sqlmodel.sql.expression import desc
from global_varibles import PAGE_LIMIT
from crud import (get_properties_in_radius, get_roles,
                  get_user_profile,individual_property_details)
from models import Property
from session import get_session
search_bp = Blueprint("search", __name__)
logger=logging.getLogger(__name__)
api = Api(search_bp)


class Search_properties(Resource):
    def post(self):
        try:
            logger.debug("searching for properties")
            data = request.json
            # data=request.args.to_dict()
            if not data:
                logger.debug("data not provided for searching")
                return {"status": "fail", "message": "data not provided"}, 400
            logger.info(f"search data:{data}")
            req_by = data.get("req_by", None)
            offset = data.get("offset", 0)
            with get_session() as session:
                is_admin = False
                if req_by:
                    user_obj = get_user_profile(user_id=req_by,
                                                session=session)
                    if user_obj and user_obj.role in ['admin' ,'staff']:
                        is_admin = True
                logger.debug(f"is_admin:{is_admin}")
                property_columns = [1 == 1]
                data_to_search = {}
                for key, value in data["body"].items():
                    if value =='':
                        pass
                    elif  not is_admin and key not in ["updated_by", "notified", "v_status", "own_name","med_name"]:
                        if hasattr(Property, key):
                            data_to_search[key] = value
                            property_columns.append(getattr(Property, key) == value)
                    elif  is_admin:
                        if hasattr(Property, key):
                            data_to_search[key] = value
                            property_columns.append(
                                getattr(Property, key) == value)
                total_properties_count = 0
                prop_query = select(Property).where(and_(*property_columns)).limit(0)
                if "price_range" in data["body"]:
                    min_price = data["body"]["price_range"]["min"]
                    logger.debug(f"min_price:{min_price}")
                    max_price = data["body"]["price_range"]["max"]
                    logger.debug(f"max_price:{max_price}")
                    if min_price and max_price:
                        if not is_admin:
                            prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price),(Property.v_status==True),(Property.status=="active"))).scalar()
                        else:
                            prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price))).scalar()
                    elif min_price and not max_price:
                        if not is_admin:
                            prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf')),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf')),(Property.v_status==True),(Property.status=="active"))).scalar()
                        else:
                            prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf'))).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf')))).scalar()
                    elif max_price and not min_price:
                        if not is_admin:
                            prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(0, max_price),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(0, max_price),(Property.v_status==True),(Property.status=="active"))).scalar()
                        else:
                            prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(0, max_price)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(0, max_price))).scalar()
                    elif len(property_columns) > 1:
                        if not is_admin:
                            prop_query = select(Property).where(and_(*property_columns),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.v_status==True),(Property.status=="active"))).scalar()
                        else:
                            prop_query = select(Property).where(and_(*property_columns)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                            if offset == 0:
                                total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns))).scalar()
                elif len(property_columns) > 1:
                    if not is_admin:
                        prop_query = select(Property).where(and_(*property_columns),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.v_status==True),(Property.status=="active"))).scalar()
                    else:
                        prop_query = select(Property).where(and_(*property_columns)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns))).scalar()
                prop_objs = session.execute(prop_query).scalars().all()
                logger.debug("Fetching all properties")
                properties = self.process_properties(prop_objs=prop_objs, is_admin=is_admin)
                logger.info(f"total_properties_count:{total_properties_count}")
                return {
                    "status": "success",
                    "property": properties,
                    "total_properties": total_properties_count,
                }
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while Searching: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while Searching: {e}")
            return {"status":"fail","message":"Internall Error"},500
    def get(self):
        try:
            logger.debug("searching for properties")
            # data = request.json
            data=request.args.to_dict()
            if not data:
                logger.info("data not provided for searching")
                return {"status": "fail", "message": "data not provided"}, 400
            logger.debug(f"search data:{data}")
            req_by = data.get("req_by", None)
            offset =int(data.get("offset", 0))
            with get_session() as session:
                is_admin = False
                if req_by:
                    user_obj = get_user_profile(user_id=req_by,
                                                session=session)
                    if user_obj and user_obj.role in ['admin' ,'staff']:
                        is_admin = True
                logger.debug(f"is_admin:{is_admin}")
                property_columns = [1 == 1]
                data_to_search = {}
                for key, value in data.items():
                    if value =='':
                        pass
                    elif  not is_admin and key not in ["updated_by", "notified", "v_status", "own_name","med_name"]:
                        if hasattr(Property, key):
                            data_to_search[key] = value
                            property_columns.append(getattr(Property, key) == value)
                    elif  is_admin:
                        if hasattr(Property, key):
                            data_to_search[key] = value
                            property_columns.append(
                                getattr(Property, key) == value)
                total_properties_count = 0
                prop_query = select(Property).where(and_(*property_columns)).limit(0)
                min_price = data.get("min",None)
                logger.info(f"min_price:{min_price}")
                max_price = data.get("max",None)
                logger.info(f"max_price:{max_price}")
                if min_price and max_price:
                    min_price=float(min_price)
                    max_price=float(max_price)
                    if not is_admin:
                        prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0: 
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price),(Property.v_status==True),(Property.status=="active"))).scalar()
                    else:
                        prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, max_price))).scalar()
                elif min_price and not max_price:
                    min_price=float(min_price)
                    if not is_admin:
                        prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf')),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf')),(Property.v_status==True),(Property.status=="active"))).scalar()
                    else:
                        prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf'))).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(min_price, float('inf')))).scalar()
                elif max_price and not min_price:
                    max_price=float(max_price)
                    if not is_admin:
                        prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(0, max_price),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(0, max_price),(Property.v_status==True),(Property.status=="active"))).scalar()
                    else:
                        prop_query = select(Property).where(and_(*property_columns),(Property.price * Property.size).between(0, max_price)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.price * Property.size).between(0, max_price))).scalar()
                elif len(property_columns) > 1:
                    if not is_admin:
                        prop_query = select(Property).where(and_(*property_columns),(Property.v_status==True),(Property.status=="active")).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns),(Property.v_status==True),(Property.status=="active"))).scalar()
                    else:
                        prop_query = select(Property).where(and_(*property_columns)).order_by(desc(Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
                        if offset == 0:
                            total_properties_count = session.execute(select(func.count(Property.p_id)).filter(and_(*property_columns))).scalar()
                prop_objs = session.execute(prop_query).scalars().all()
                logger.info("Fetching all properties")
                properties = self.process_properties(prop_objs=prop_objs, is_admin=is_admin)
                logger.info(f"total_properties_count:{total_properties_count}")
                return {
                    "status": "success",
                    "property": properties,
                    "total_properties": total_properties_count,
                }
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while Searching: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while Searching: {e}")
            return {"status":"fail","message":"Internall Error"},500

    def put(self):
        try:
            logger.debug("searching properties by latitude and longitude")
            # data = request.args.to_dict()
            data=request.json
            if not data:
                logger.warning("data not provided to get properties by latitude and logtitude")
                return {"status":"fail","message":"data not provided to get properties by latitude and longitude"}
            logger.info(f"data to search properties by latitiude and longitude:{data}")
            req_by = data.get("req_by", None)
            latitude = data.get("latitude", None)
            longitude = data.get("longitude", None)
            if not req_by or not latitude or not longitude:
                logger.warning("required paramters are not provided to search property by lat and long")
                return {
                    "status": "fail",
                    "message": "plese provide user id,latitude and longitude"
                }, 400

            with get_session() as session:
                user_obj = get_user_profile(user_id=req_by, session=session)
                if not user_obj:
                    logger.info(f"user {req_by} not found")
                    return {
                        "status": "fail",
                        "message": "user not found"}, 400
                roles = get_roles()
                rol_auth = 0
                requested_role = user_obj.role
                logger.info(f"requsted_role:{requested_role}")
                if requested_role.lower() == "user":
                    active_notifications = user_obj.active_notifications
                    if active_notifications > 0:
                        rol_auth = roles["active_notifications"]
                else:
                    rol_auth = roles[requested_role.lower()]
                logger.debug(f"user with:{rol_auth} seraching propeties by lat and long")
                if rol_auth <= 1:
                    return {"status": "success", "properties": []},200
                properties = []
                prop_objs = get_properties_in_radius(lat=float(latitude),
                                                     lon=float(longitude),
                                                     session=session)
                if prop_objs:
                    for prop_obj in prop_objs:
                        prop_imgs = []
                        for image_objs in prop_obj.all_prop_imgs:
                            if image_objs:
                                prop_imgs.append(image_objs.img_url)
                            break
                        property = {
                            "landmark": prop_obj.landmark,
                            "district": prop_obj.district,
                            "listing_type": prop_obj.listing_type,
                            "unit": prop_obj.unit,
                            "area": prop_obj.size,
                            "unit_price": prop_obj.price,
                            "prop_type": prop_obj.p_type,
                            "latitude": prop_obj.latitude,
                            "longitude": prop_obj.longitude,
                            "property_id": prop_obj.p_id,
                            "village": prop_obj.village,
                            "prop_image": prop_imgs
                        }
                        properties.append(property)
            logger.info(f"properties :{properties}")
            return {"status": "success", "properties": properties}
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while Searching by lat and long: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while Searching by lat and long: {e}")
            return {"status":"fail","message":"Internall Error"},500

        
    def process_properties(self, prop_objs, is_admin):
        properties = []
        if is_admin:
            for prop_obj in prop_objs:
                property_details=individual_property_details(property_obj=prop_obj,is_admin=is_admin,is_image_ids_required=False)
                property = property_details["property"]
                properties.append(property)
        else:
            for prop_obj in prop_objs:
                prop_image = []
                for img_obj in prop_obj.all_prop_imgs:
                    if img_obj:
                        prop_image.append(img_obj.img_url)
                        break
                property = {
                    "landmark": prop_obj.landmark,
                    "district": prop_obj.district,
                    "listing_type": prop_obj.listing_type,
                    "p_created_on": str(prop_obj.p_created_on),
                    "unit": prop_obj.unit,
                    "area": prop_obj.size,
                    "p_id": prop_obj.p_id,
                    "unit_price": prop_obj.price,
                    "prop_type": prop_obj.p_type,
                    "prop_images": prop_image
                }
                properties.append(property)
        return properties



api.add_resource(Search_properties, '/search')
