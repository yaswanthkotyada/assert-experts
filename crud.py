from sqlmodel import select, update, delete, desc,or_,and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from math import radians, cos, sin, asin, pi
from models import User,District,Payment,Property, Property_img, Area,State,Propert_Price_History,Payment,WhatsappAds
from session import get_session
from global_varibles import DOCUMENT_SIZE,PLAN_FEES,DEFAULT_PROPERTY_URLS_FOR_WHATSAPP,DEFAULT_ADS,ACCESS_TOKEN,PHONE_NUMBER_ID_FOR_WHATSAPP,PAGE_LIMIT,PROPERTIES_AROUND_KM,COUNT_OF_RECENT_PROPERTIES,whatsapp_template_names
import random
import os
import pytz
import logging
import uuid
import time
import mimetypes
from sqlalchemy import func
from werkzeug.utils import secure_filename
from flask import request, current_app,json
import requests
from datetime import datetime

areas_in_telugu="areas_in_Telugu.json"

logger=logging.getLogger(__name__)

def add_user(data,session):
    try:
        logger.debug("adding user")
        query=User(**data)
        session.add(query)
        session.commit()
        logger.debug(f"user {query.id} added successfully")
        return query.id
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e


def get_user_profile(user_id, session):
    try:
        logger.debug(f"gettting user profile for {user_id}")
        user_obj = session.execute(
            select(User).where(User.id == user_id)).scalar()
        return user_obj
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    
def create_a_order(session,data_to_add):
    try:
        logger.debug("creating a oredr")
        query=Payment(**data_to_add)
        session.add(query)
        session.commit()
        logger.debug(f"order {query.u_id} created successfully")
        paymenty_data={
                        "payment_id":query.id,
                        "payment_gateway":query.payment_gateway,
                        "price":query.price,
                        "order_id":query.order_id,
                        "transaction_id":query.transaction_id,
                        "payment_date":str(query.payment_date),
                        "from_date":str(query.from_date),
                        "to_date":str(query.to_date),
                        "subscription_plan_type":query.subscription_plan_type,
                        "Payment_status":query.Payment_status,
                        "comments":query.comments
                    }
        return paymenty_data
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    
    
#this duplicate functions is created to decrese the complexity of checking user existance every time
def get_user_profile_for_buttons(session,ph_number):
    try:
        logger.debug(f"checking for the user existance with {ph_number}")
        query=select(User).filter(or_(User.id==ph_number,User.ph_num_1==ph_number,User.ph_num_2==ph_number))
        user_obj=session.execute(query).scalar()
        if user_obj and user_obj.ph_num_1 !=int(ph_number):
            logger.debug("swaping user phone number")
            data_to_update = {"ph_num_1": int(ph_number),
                              "ph_num_2":user_obj.ph_num_1}
            update_user_profile_for_whatsapp_users(session=session, user_id=user_obj.id, data_to_update=data_to_update)
        return user_obj
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e 
    
#the following function is used during for whatsapp flow 

def get_user_profile_for_whatsapp_users(session,ph_number):
    try:
        logger.debug(f"checking for the user existance with {ph_number}")
        query=select(User).filter(or_(User.id==ph_number,User.ph_num_1==ph_number,User.ph_num_2==ph_number))
        user_obj=session.execute(query).scalar()
        return user_obj
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e 
    
def update_user_profile_for_whatsapp_users(session,user_id,data_to_update):
    try:
        logger.debug(f"updating profile of user : {user_id}")
        query = update(User).where(User.id == user_id).values(data_to_update)
        session.execute(query)
        session.commit()
        logger.debug("User profile updated successfully")
        return {"status":"success","message":"user addded successfully"},201
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e

def update_profile(user_id, data_to_update, session):
    try:
        logger.debug(f"updating user {user_id}")
        query = update(User).where(User.id == user_id).values(data_to_update)
        session.execute(query)
        session.commit()
        logger.debug("User updated successfully")
        return {'status': 'success'},200  
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e


def update_property(property_id, data_to_update, session):
    try:
        logger.debug(f"updating property of : {property_id}")
        logger.debug(f"data_to_update:{data_to_update}")
        query = update(Property).where(
            Property.p_id == property_id).values(data_to_update)
        session.execute(query)
        session.commit()
        logger.debug("Property updated successfully")
        return {"status": "success","message":"Property updated successfully"}, 201
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e


def get_property_object(property_id, session):
    try:
        logger.debug(f"gettting property_object for property_id{property_id}")
        prop_obj = session.execute(
            select(Property).where(Property.p_id == property_id)).scalar()
        return prop_obj
    except Exception as e:
        raise e


def get_image_object(image_id, session):
    try:
        logger.debug(f"gettting image object for image_id :{image_id}")
        img_obj = session.execute(
            select(Property_img).where(
                Property_img.img_id == image_id)).scalar()
        logger.debug(f"image object :{img_obj}")
        return img_obj
    except Exception as e:
        raise e


def delete_property_img(image_id, session):
    try:
        logger.debug(f"Deleting property image :{image_id}")
        query = delete(Property_img).where(Property_img.img_id == image_id)
        session.execute(query)
        session.commit()
        logger.debug("Image deleted successfully")
        return {"status": "Image deleted successfully"}, 201
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    
    
def individual_property_details(property_obj,is_admin,is_image_ids_required=True):
    try:
        logger.debug("getting property details")
        prop_images = []
        if is_image_ids_required:
            for image_obj in property_obj.all_prop_imgs:
                prop_images.append({"img_id":image_obj.img_id,"img_url":image_obj.img_url})
        else:
            for image_obj in property_obj.all_prop_imgs:
                prop_images.append(image_obj.img_url)
        developments=[]
        if  property_obj.developments: 
            developments=property_obj.developments.split(',')
        if len(developments)==0:
            developments=""
        documents=property_obj.docFile
        if documents:
            documents=documents.split(',')
        else:
            documents=[]
        data={"property": {
            "listing_type": property_obj.listing_type,
            "user_id":property_obj.cont_user_id,
            "p_id": property_obj.p_id,
            "p_type": property_obj.p_type,
            "size": property_obj.size,
            "unit": property_obj.unit,
            "prop_name":property_obj.prop_name,
            "bhk":property_obj.bhk,
            "price": property_obj.price,
            "dimensions": property_obj.dimensions,
            "direction": property_obj.direction,
            "est_year": property_obj.est_year,
            "latitude": property_obj.latitude,
            "longitude": property_obj.longitude,
            "state": property_obj.state,
            "district": property_obj.district,
            "village": property_obj.village,
            "landmark": property_obj.landmark,
            "ad_info": property_obj.ad_info,
            "developments": developments,
            "med_name": property_obj.med_name,
            "med_num1": property_obj.med_num1,
            "med_num2": property_obj.med_num2,
            "own_name":property_obj.own_name,
            "own_num1":property_obj.own_num1,
            "own_num2":property_obj.own_num2,
            "docfile":documents,
            "rera":property_obj.rera,
            "lift":property_obj.lift,  
            "furnshied":property_obj.furnshied,
            "bound_wall":property_obj.bound_wall,
            "num_open_sides":property_obj.num_open_sides,
            "loan_eligible":property_obj.loan_eligible,
            "approved_by":property_obj.approved_by,
            "survey_number":property_obj.survey_number,
            "doc_num":property_obj.doc_num,
            "disputes":property_obj.disputes,
            "reg_loc":property_obj.reg_loc,
            "property_name":property_obj.prop_name,
            "v_status":property_obj.v_status,
            "govt_price":property_obj.govt_price,
            "rating":property_obj.rating,
            "num_of_leads":property_obj.num_of_leads,
            "p_created_on":str(property_obj.p_created_on),
            "status":property_obj.status,
            "comments":property_obj.comments,
            "parking": property_obj.parking,
            "images": prop_images}
            }
        if is_admin:
            data["property"]["v_status"]=property_obj.v_status
            data["property"]["v_comments"]=property_obj.v_comments
            data["property"]["updated_by"]=property_obj.updated_by
            data["property"]["property_updated_on"]=str(property_obj.p_updated_on)
            data["property"]["notified"]=property_obj.notified
            
        logger.debug(f"property details:{data}")
        return data
    except Exception as e:
        raise e


def get_property_details(prop_object_req,session,is_admin):
    try:
        logger.debug(f"getting property details for property:{prop_object_req}")
        latitude = prop_object_req.latitude
        longitude = prop_object_req.longitude
        recomended_prop = []
        if latitude and longitude:
            prop_objs = get_properties_in_radius(lat=latitude, lon=longitude,session=session)
            if prop_objs:
                requsted_prop_id=prop_object_req.p_id
                for prop_obj in prop_objs:
                    if prop_obj.p_id !=requsted_prop_id:
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
                            "p_id": prop_obj.p_id,
                            "village": prop_obj.village,
                            "p_created_on":str(prop_obj.p_created_on),
                            "prop_image": prop_imgs
                        }
                        recomended_prop.append(property)
        # recent properties
        rec_prop_objs = get_latest_properties(session)
        rec_properties = []                        
        for prop_obj in rec_prop_objs:
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
                "p_id": prop_obj.p_id,
                "p_created_on":str(prop_obj.p_created_on),
                "prop_images": prop_imgs
            }
            rec_properties.append(property)
        data=individual_property_details(property_obj=prop_object_req,is_admin=is_admin,is_image_ids_required=False)
        return {"status": "sucess", "data": data,
            "recomended_prop": recomended_prop,
            "recent_properties": rec_properties}
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
       raise e


def get_home_page_properties(listing_type, session,offset):
    try:
        logger.debug(f"getting properties of listing type:{listing_type}")
        query = select(Property).where(and_(
            Property.listing_type == listing_type,
            Property.status == "active",Property.v_status==True)).order_by(desc(
                Property.p_created_on)).offset(offset).limit(PAGE_LIMIT)
        prop_objs = session.execute(query).scalars().all()
        return {"prop_objs":prop_objs}
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e


def get_latest_properties(session):
    try:
        logger.debug("sending latest properties in data base")
        query = select(Property).where(and_(Property.status=="active",Property.v_status==True)).order_by(desc(Property.p_created_on)).limit(COUNT_OF_RECENT_PROPERTIES)
        prop_objs=session.execute(query).scalars().all()
        return prop_objs
    except SQLAlchemyError as se:
        raise se
    except Exception as e:
        raise e





def get_properties_in_radius(lat, lon, session, radii=PROPERTIES_AROUND_KM):
    try:
        logger.debug("processing for properties in the radius")
        radius_meters = radii * 1000
        # Earth radius in meters
        earth_radius = 6371000  # in meters
        logger.debug(f"latitude:{lat}")
        logger.debug(f"longitutde:{lon}")
        # Convert latitude and longitude from degrees to radians
        lat_rad = radians(lat)
        lon_rad = radians(lon)
        # Calculate the maximum latitude difference
        max_lat_diff = radius_meters / earth_radius
        # Calculate the maximum longitude difference
        max_lon_diff = asin(sin(max_lat_diff) / cos(lat_rad))
        # Convert latitude and longitude differences from radians to degrees
        max_lat_diff_deg = max_lat_diff * (180 / pi)
        max_lon_diff_deg = max_lon_diff * (180 / pi)
        # Calculate latitude and longitude ranges
        lat_range = (lat - max_lat_diff_deg, lat + max_lat_diff_deg)
        lon_range = (lon - max_lon_diff_deg, lon + max_lon_diff_deg)
        # Print latitude and longitude ranges
        logger.debug(f"Latitude Range:{lat_range}")
        logger.debug(f"Longitude Range:{lon_range}")
        # Execute query to retrieve property IDs
        query = select(Property).where(
            Property.latitude.between(lat_range[0], lat_range[1]),
            Property.longitude.between(lon_range[0], lon_range[1]),Property.status=="active",Property.v_status==True).limit(COUNT_OF_RECENT_PROPERTIES)
        prop_objs = session.execute(query).scalars().all()
        logger.debug("sending releted properties")
        # Return property IDs
        if not prop_objs:
            return None
        return prop_objs
    except SQLAlchemyError as se:
        raise se
    except Exception as e:
        raise e
    
def convert_to_utc(date_str):
    try:
        local_datetime = datetime.strptime(date_str, "%d/%m/%Y")
        ist_tz = pytz.timezone('Asia/Kolkata')
        local_datetime = ist_tz.localize(local_datetime)
        utc_datetime = local_datetime.astimezone(pytz.utc)
        return utc_datetime
    except Exception as e:
        logger.warning("date is not provided in required format ('%d/%m/%Y')")
        raise e


def read_file(file_name):
    try:
        logger.debug(f"opening file {file_name}")
        with open(file_name, 'r') as file:
            content = file.read()
            return content
    except Exception as e:
        logger.critical(f"failed to open {file_name}")
        raise e

def read_json_file(file_name):
    try:
        logger.debug(f"opening file {file_name}")
        if not os.path.exists(file_name):
        # If the file doesn't exist, create it with an empty dictionary
            with open(file_name, 'w') as file:
                json.dump({}, file)
            return {}
        with open(file_name, 'r', encoding='utf-8') as file:
            content = json.load(file)
            return content
    except Exception as e:
        logger.critical(f"failed to open {file_name}")
        raise e

def get_user_ph_nums(district, landmark, session):
    try:
        logger.debug(f"getting user phone numbers for the area:{landmark}")
        query_1 = select(Area).where(and_(Area.district_id == district,Area.name=="All Areas"))
        query_2 = select(Area).where(Area.name == landmark)
        all_district_obj = session.execute(query_1).scalar()
        area_obj = session.execute(query_2).scalar()
        logger.debug(f"all_areas_id:{all_district_obj},area_id of {landmark}:{area_obj}")
        area_id=None
        ph_numbers = []
        if all_district_obj:
            for user_obj in all_district_obj.users:
                # if user_obj.active_notifications>0:
                ph_numbers.append({"ph_num":user_obj.ph_num_1,"langauge":user_obj.prefered_langauge})
        if area_obj:
            area_id=area_obj.id
            for user_obj in area_obj.users:
                if user_obj:
                    # active_notifications=user_obj.active_notifications
                    # if active_notifications>0:
                    ph_numbers.append({"ph_num":user_obj.ph_num_1,"langauge":user_obj.prefered_langauge})
                    num_of_notifications_notified=user_obj.num_of_notifications_notified
                    # active_notifications-=1  and put this update query
                    logger.debug(f"number of times notified:{num_of_notifications_notified}")
                    if not num_of_notifications_notified:
                        num_of_notifications_notified=0
                    num_of_notifications_notified+=1
                    session.execute(update(User).where(User.id==user_obj.id).values(num_of_notifications_notified=num_of_notifications_notified))
        session.commit()
        logger.debug(f"users ph_numbers for the area {landmark} :{ph_numbers}")
        return {"ph_numbers":ph_numbers,"area_id":area_id}
    except Exception as e:
        logger.critical(f"failed to get user phonenumbers:{e}")
        raise e


def send_property_card_in_telugu(property_id,img_url, params_in_telugu,phone_num):
    try:
        logger.debug(f"sending property {property_id} to whatsaapp users")
        visit_property = f"property_ind?prop_id={property_id}"
        template_names=whatsapp_template_names()
        template_name=template_names.get("property_notification_temp_in_telugu",None)
        if not template_name:
            raise ValueError("telugu template name not availble") 
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone_num),
            "type": "template",
            "template": {
                "name":template_name,
                "language": {
                    "code": "te"
                },
                "components": [{
                    "type":"header",
                    "parameters": [{
                        "type": "image",
                        "image": {
                            "link": img_url
                        }
                    }]
                }, {
                    "type":"body",
                    "parameters":params_in_telugu
                }, {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [{
                        "type": "text",
                        "text": visit_property
                    }]
                }]
            }
        }
        response = requests.post(
                f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
                headers={
                    "Authorization":f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                    },
                json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
    except ValueError as ve:
        raise ve
    except Exception as e:
        logger.critical(f"failed to send property card in telugu:{e}")
        raise e

def send_property_card_in_english(property_id,img_url, params_in_english,phone_num):
    try:
        visit_property = f"property_ind?prop_id={property_id}"
        template_names=whatsapp_template_names()
        template_name=template_names.get("property_notification_temp_in_english",None)
        if not template_name:
            raise ValueError("english template name not availble") 
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone_num),
            "type": "template",
            "template": {
                "name":template_name,
                "language": {
                    "code": "en"
                },
                "components": [{
                    "type":"header",
                    "parameters": [{
                        "type": "image",
                        "image": {
                            "link": img_url
                        }
                    }]
                }, {
                    "type":"body",
                    "parameters":params_in_english
                }, {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [{
                        "type": "text",
                        "text": visit_property
                    }]
                }]
            }
        }
        response = requests.post(
                f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
                headers={
                    "Authorization":f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                    },
                json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
        
    except Exception as e:
        logger.critical(f"failed to send property card in english:{e}")
        raise e
    
def send_interest_property_in_english(property_id, params_in_english,phone_num):
    try:
        visit_property = f"property_ind?prop_id={property_id}"
        template_names=whatsapp_template_names()
        template_name=template_names.get("interest_property_in_english",None)
        if not template_name:
            raise ValueError("interest template name not availble") 
        payload = {
            "messaging_product": "whatsapp",
            "to": str(phone_num),
            "type": "template",
            "template": {
                "name":template_name,
                "language": {
                    "code": "en"
                },
                "components": [ {
                    "type":"body",
                    "parameters":params_in_english
                }, {
                    "type": "button",
                    "sub_type": "url",
                    "index": 0,
                    "parameters": [{
                        "type": "text",
                        "text": visit_property
                    }]
                }]
            }
        }
        response = requests.post(
                f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
                headers={
                    "Authorization":f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                    },
                json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
        
    except Exception as e:
        logger.critical(f"failed to send property card in english:{e}")
        raise e
    
def send_message_template_to_mediator(name,requested_user_ph_num,mediator_phone_num):
    try:
        template_names=whatsapp_template_names()
        template_name=template_names.get("temp_to_mediator",None)
        if not template_name:
            raise ValueError("interest template name not availble") 
        payload = {
            "messaging_product": "whatsapp",
            "to": str(mediator_phone_num),
            "type": "template",
            "template": {
                "name":template_name,
                "language": {
                    "code": "en"
                },
                "components": [ {
                    "type":"body",
                    "parameters":[
                            {"type":"text","text":name},
                            {"type":"text","text":requested_user_ph_num}
                            ]
                }]
            }
        }
        response = requests.post(
                f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
                headers={
                    "Authorization":f"Bearer {ACCESS_TOKEN}",
                    "Content-Type": "application/json"
                    },
                json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
        
    except Exception as e:
        logger.critical(f"failed to send property card in english:{e}")
        raise e


def generate_areas():
    try:
        logger.debug("generating all the areas")
        areas_supporting={}
        with get_session() as session:
            state_query=select(State)
            state_objs=session.execute(state_query).scalars().all()
            for state_obj in state_objs:
                if len(state_obj.districts)>0:
                    areas_supporting[state_obj.id]={}
                    for district_obj in state_obj.districts:
                        areas_supporting[state_obj.id][district_obj.id]=[]
                        for area_obj in district_obj.areas:
                            areas_supporting[state_obj.id][district_obj.id].append({"id":area_obj.id,"title":area_obj.name})
            logger.debug(f"areas_supporting:{areas_supporting}")
            return areas_supporting
    except SQLAlchemyError as se:
        logger.error(f"sqlalchemy error while generating areas:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed too generate areas:{e}")
        raise e


def get_roles():
    roles={
        "guest":0,
        "user":1,
        "active_notifications":2,
        "classic":3,
        "premium":4,
        "staff":5,
        "admin":6
    }
    return roles


def get_all_user_profiles(session,offset):
    try:
        logger.debug("sending all user profiles")
        total_count=0
        if offset==0:
            count_query=select(func.count(User.id))
            total_count = session.execute(count_query).scalar()
        query=select(User).order_by(desc(User.created_on)).offset(offset).limit(PAGE_LIMIT)
        user_objs=session.execute(query).scalars().all()
        return {"user_objs":user_objs,"total_count":total_count}
    except SQLAlchemyError as se:
        logger.error(f"Sqlalchemy error while getiing all user profiles:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to load all user profiles:{e}")
        raise e


def to_dict(obj):
    try:
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: to_dict(value) for key, value in obj.items()}
        elif hasattr(obj, '__dict__'):
            return {key: to_dict(value) for key, value in obj.__dict__.items()}
        else:
            return obj
    except Exception as e:
        raise e


def execute_query(query, session,offset):
    try:
        logger.debug(f"executing the query:{query}")
        data_objs=session.execute(query).offset(offset).limit(PAGE_LIMIT)
        return data_objs
    except Exception as e:
        logger.critical(f"failed to exceute query:{e}")
        raise e

def get_count_of_plots_flats(session):
    try:
        logger.debug("sending count of flats,plots,commercial lands")
        plots_count=session.execute(select(func.count(Property.p_id)).filter(Property.p_type=="plot")).scalar()
        flat_count=session.execute(select(func.count(Property.p_id)).filter(Property.p_type=="flat")).scalar()
        commercial_count=session.execute(select(func.count(Property.p_id)).filter(Property.p_type=="commercial")).scalar()
        agricultural_count=session.execute(select(func.count(Property.p_id)).filter(Property.p_type=="agricultural lands")).scalar()
        logger.debug(f"plots_count:{plots_count},flats_count:{flat_count},commercial_count:{commercial_count},agricultural_count:{agricultural_count}")
        return {"plots_count":plots_count,"flats_count":flat_count,"commercial_count":commercial_count,"agricultural_count":agricultural_count}
    except SQLAlchemyError as se:
        logger.error(f"sqlalchemy error while counting properties:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to load count plots,flats:{e}")
        raise e

def add_Propert_Price_History(session,old_price,property_id):
    try:
        logger.debug(f"adding property price history of property:{property_id}")
        query=Propert_Price_History(prop_id=property_id,
                                              old_price=old_price)
        session.add(query)
        session.commit()
        logger.debug("property price history added successfully")
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e

def add_property_documents(documents,allowed_extensions,property_id,property_type,document_number,mediator_number,property_location):
    try:
        logger.debug(f"adding documents for property :{property_id}")
        errors = []
        doc_urls=[]
        for document in documents:
            file_name = secure_filename(document.filename)
            doc_type = mimetypes.guess_type(file_name)
            logger.debug(f"document_type:{doc_type[0]}")
            if doc_type[0] not in allowed_extensions :
                logger.warning({"message": "Invalid File Type"})
                errors.append(f"Invalid File Type :{file_name}")
                continue 
            file_data = document.read()
            max_file_size = DOCUMENT_SIZE
            if len(file_data) > max_file_size:
                logger.warning({"message": "file size exceeds"})  
                errors.append(f"file size exceeds:{file_name}")
                continue        
            logger.debug(f"document size:{len(file_data)}")
            folder_name = current_app.config['UPLOAD_FOLDER']
            folder_name+="/documents"
            property_id_for_name=str(property_id)
            property_type=property_type
            document_number=str(document_number) 
            property_location=property_location or "assert_experts"
            mediator_number=str(mediator_number)
            name, ext = file_name.rsplit('.', 1)
            file_name=property_id_for_name+"_"+property_type+"_"+document_number+"_"+property_location+"_"+mediator_number+"_"+name+"."+ext
            logger.debug(f"folder_name:{folder_name}")
            logger.debug(f"file_name:{file_name}")
            absolute_path = os.path.join(folder_name, file_name)
            logger.debug(f"abs_path: {absolute_path}")
            with open(absolute_path, 'wb') as f:
                f.write(file_data)
            base_url = request.url_root
            relative_path = os.path.relpath(absolute_path, folder_name)
            logger.debug(f"reltive_pathe:{relative_path }")
            doc_url = os.path.join(base_url, 'files/documents', relative_path)
            logger.debug(f"doc_url: {doc_url}")
            doc_urls.append(doc_url)
        res_urls_string=",".join(doc_urls)
        logger.debug(f"documents_urls:{res_urls_string}")
        return {"res_urls_string":res_urls_string,"errors":errors}
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e

def generate_order_id():
    logger.debug("generating order id")
    timestamp = int(time.time() * 1000)
    random_part = uuid.uuid4().hex[:8]
    order_id = f"ORD-{timestamp}-{random_part}"
    return order_id

def create_a_oreder(user_id,plan_type):
    try:
        logger.debug(f"creating order of user:{user_id}")
        with get_session() as session:
            user_obj=get_user_profile_for_buttons(ph_number=user_id,session=session)
            order_id=generate_order_id()
            plan_value=PLAN_FEES[plan_type]["value"]
            if not user_obj:
                user_date={"id":user_id}
                user_id=add_user(data=user_date,session=session)
            else:
                user_id=user_obj.id
            payment_obj=Payment(u_id=user_id,order_id=order_id,subscription_plan_type=plan_type,price=plan_value)
            session.add(payment_obj)
            session.commit()
            logger.debug(f"order created successfully with order id:{order_id}")
            return order_id
    except IntegrityError as e:
        logger.error(f"integriity error while creating order :{e}")
        raise e
    except SQLAlchemyError as se:
        logger.error(f"sqlalchemy error while creating order :{se}")
        raise se
    except Exception as e:
        raise e
    
def get_pmt_obj(session,pmt_id):
    try:
        payment_query=select(Payment).where(Payment.id==pmt_id)
        pmt_obj=session.execute(payment_query).scalar()
        return pmt_obj
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    
def get_order_obj(session,order_id):
    try:
        payment_query=select(Payment).where(Payment.order_id==order_id)
        pmt_obj=session.execute(payment_query).scalar()
        return pmt_obj
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
def update_pmt_obj(session,pmt_id,data_to_update):
    try:
        logger.debug("updating a oreder")
        query=update(Payment).where(Payment.id==pmt_id).values(data_to_update)
        session.execute(query)
        session.commit()
        logger.debug("oreder updated successfully")
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
        

def update_payment_status(order_id,transaction_id,transaction_type,price):
    try:
        with get_session() as session:
            logger.debug(f"updating payment status for order_id:{order_id}")
            pmt_obj=get_order_obj(session=session,order_id=order_id)
            if not pmt_obj:
                logger.critical(f"order not exists with order id {order_id}")
                raise Exception(f"order not exists with order id {order_id}")
            pmt_id=pmt_obj.id
            user_id=pmt_obj.u_id
            subscription_plan_type=pmt_obj.subscription_plan_type
            Payment_status="paid"
            pmt_period=PLAN_FEES[subscription_plan_type]["period_in_months"]
            num_of_notifications=PLAN_FEES[subscription_plan_type]["number_of_notifications"]
            plan_starts_at,plan_ends_at=get_start_end_dates(pmt_period)
            start_date_time_obj=datetime.strptime(plan_starts_at, "%d-%m-%y")
            end_date_time_obj=datetime.strptime(plan_ends_at, "%d-%m-%y")
            query=update(Payment).where(Payment.id==pmt_id).values(transaction_id=transaction_id,
                payment_gateway=transaction_type,price=price,Payment_status=Payment_status,from_date=start_date_time_obj,to_date=end_date_time_obj,payment_date=start_date_time_obj)
            session.execute(query)
            user_obj=get_user_profile(user_id=user_id,session=session)
            if not user_obj:
                logger.critical(f"user not exists with user_id {user_id} to update the notifications")
                raise Exception(f"order not exists with user_id {user_id} to update the notifications")
            present_active_notifications=user_obj.active_notifications
            data_to_update={
                "active_notifications":present_active_notifications+num_of_notifications
            }
            update_user_profile_for_whatsapp_users(session=session,user_id=user_id,data_to_update=data_to_update)
            logger.debug("payment updated suucessfully")
            return {"subscription_plan_type":subscription_plan_type,"plan_starts_at":plan_starts_at,"plan_ends_at":plan_ends_at}
    except IntegrityError as e:
        raise e
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e

def get_start_end_dates(months):
   try:
        start_date = datetime.now()
        new_month = start_date.month + months
        new_year = start_date.year + new_month // 12
        new_month = new_month % 12
    
        if new_month == 0:
            new_month = 12
            new_year -= 1
        # Formating the dates as "day-month-year"
        end_date = datetime(new_year, new_month, start_date.day)
        start_date_formatted = start_date.strftime("%d-%m-%y")
        end_date_formatted = end_date.strftime("%d-%m-%y")
        
        return start_date_formatted, end_date_formatted
   except Exception as e:
       raise e
   
    


def get_add_description(area_name):
    try:
        logger.debug("getting add description for whatsapp")
        with get_session() as session:
            query=select(WhatsappAds).where(WhatsappAds.number_of_notifications>0)
            ad_objs=session.execute(query).scalars().all()
            add_desc=None
            if ad_objs:
                for ad_obj in ad_objs:
                    project_areas_str=ad_obj.project_areas
                    areas=project_areas_str.split(',')
                    if area_name in areas:
                        add_desc=ad_obj.ad_description
                        break
            logger.debug(f"add description:{add_desc}")
            return add_desc
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e


def get_parameters_for_property_card(area_id,property_type,listing_type,bhk,village,area,price,units,buy_price_range):
    try:
        logger.debug(f"get_parameters_for_property_card for property type :{property_type}")
        json_data=read_json_file(file_name=areas_in_telugu)
        units_p_type_json={"sqyd":"గజం",
                          "sqft":"చ: అడుగు",
                          "sq.m":"చదరపు మీటర్",
                          "cent":"సెంట్",
                          "acre":"ఎకరం",
                          "flat":"ఇల్లు",
                          "plot":"ప్లాట్",
                          "land":"భూమి",
                          "agriculture land":"వ్యవసాయ భూమి",
                          "pg":"పీజీ",
                          "office place":"ఆఫీస్ స్థలం",
                          "commercial place":"కమర్షియల్ స్థలం",
                          "students hostel":"విద్యార్థులు  హాస్టల్",
                          "independent house":"ఇండివిడ్యుఅల్ ఇల్లు",
                          "co working place":"కో-వర్కింగ్ స్థలం"}
        village_in_telugu=json_data.get(str(area_id),village.capitalize())
        property_type_in_telugu=units_p_type_json.get(property_type,property_type.capitalize())
        units_in_telugu=units_p_type_json.get(units,units)
        if listing_type=="buy" or listing_type=="Buy":
            price_val=buy_price_range.split("-")
            min_price,max_price=price_val[0],price_val[1]
            location_in_eng=f"Wanted {property_type.capitalize()} in {village.capitalize()}"
            location_in_tel=f"{village_in_telugu} లో {property_type_in_telugu} కావాలి"
            price_in_tel=f"బడ్జెట్ {int(min_price)} నుండి {int(max_price)} రూపాయలు/{units_in_telugu}"
            price_in_eng=f"Budget {buy_price_range} Rs/{units}"
        else:
            price=int(price)
            location_in_eng=f"{property_type.capitalize()} For Sale in {village.capitalize()}"
            location_in_tel=f"{village_in_telugu} లో {property_type_in_telugu} అమ్మకానికి ఉంది"
            if property_type=="flat":
                price_in_eng=f"{bhk}, {area} {units}, {price} Rs/{units}"
                price_in_tel=f"{bhk}, {area} {units_in_telugu} ,{price} రూపాయలు/{units_in_telugu}"
            else:
                price_in_eng=f"{area} {units}, {price} Rs/{units}"
                price_in_tel=f"{area} {units_in_telugu} ,{price} రూపాయలు/{units_in_telugu}"
        parameters_in_tel={
            "price_in_tel":price_in_tel,
            "location_in_tel":location_in_tel
        }
        parameters_in_eng={
            "location_in_eng":location_in_eng,
            "price_in_eng":price_in_eng
        } 
        logger.debug(f"parameters_in_tel:{parameters_in_tel},parameters_in_eng:{parameters_in_eng}")
        return {"parameters_in_tel":parameters_in_tel,"parameters_in_eng":parameters_in_eng,"area_name_in_tel":village_in_telugu}
    except Exception as e:
        logger.critical(f"failed to get parameters for property cards:{e}")
        raise e 
        

def send_whatsapp_notifications(prop_obj,session):
    try:
        logger.debug(f"sending whatsap notification of property:{prop_obj}")
        district = prop_obj.district
        village = prop_obj.village
        property_type=prop_obj.p_type
        property_listing=prop_obj.listing_type
        area=prop_obj.size
        buy_price_range=prop_obj.doc_num
        units=prop_obj.unit
        prop_price=prop_obj.price
        bhk=prop_obj.bhk
        property_id=prop_obj.p_id
        logger.debug(f"district:{district}")
        logger.debug(f"area:{village}")
        logger.debug(f"property:{property_type}")
        if not (property_listing and village and district and property_type and units and area):
            return {"total_users": 0, "action": False}
        elif property_listing=="sell":
            if not prop_price:
                return {"total_users":0,"action":False}
        elif property_listing=="buy":
            if not buy_price_range:
                return {"total_users":0,"action":False}
            buy_price_val=buy_price_range.split("-")
            if len(buy_price_val)!=2:
                return {"total_users":0,"action":False}
        prop_img = None
        for image_objs in prop_obj.all_prop_imgs:
            if image_objs:
                prop_img = image_objs.img_url
            break
        if prop_img:     #disucss this condition when it uploded to server
            res = prop_img.split(":")
            res[0] = "https"
            prop_img = res[0] + ":" + res[1]
            logger.debug(f"modified_prop_img:{prop_img}")
        logger.debug(f"prop_img:{prop_img}")
        
        if not prop_img:
            default_property_url=None
            if property_listing=="buy":
                default_property_url=DEFAULT_PROPERTY_URLS_FOR_WHATSAPP["buy"].get(property_type,None)
            else:    
                default_property_url=DEFAULT_PROPERTY_URLS_FOR_WHATSAPP["sell"].get(property_type,None)
            if not default_property_url:
                default_property_url=DEFAULT_PROPERTY_URLS_FOR_WHATSAPP.get("default")
            prop_img=default_property_url
        phone_nums_area_id = get_user_ph_nums(district=district,
                                            landmark=village,
                                            session=session)
        logger.debug(f"phone_nums_area_id:{phone_nums_area_id}")
        ph_numbers=phone_nums_area_id["ph_numbers"]
        area_id=phone_nums_area_id["area_id"]
        logger.debug(f"area_id:{area_id} of {village}")
        parms_obj=get_parameters_for_property_card(area_id=area_id,area=area,property_type=property_type,listing_type=property_listing,bhk=bhk,village=village,price=prop_price,units=units,buy_price_range=buy_price_range)
        parameters_in_tel=parms_obj["parameters_in_tel"]
        parameters_in_eng=parms_obj["parameters_in_eng"]
        logger.debug(f"parameters_in_tel:{parameters_in_tel}")
        logger.debug(f"parameters_in_eng:{parameters_in_eng}")
        add_description=get_add_description(area_name=village)
        if not add_description:
            add_description=random.choice(DEFAULT_ADS)
        params_in_english=[
                        {"type":"text","text":parameters_in_eng["location_in_eng"]},
                        {"type":"text","text":parameters_in_eng["price_in_eng"]},
                        {"type":"text","text":add_description},
                        {"type":"text","text":property_id}  
                        ]
        params_in_telugu=[
                    {"type":"text","text":parameters_in_tel["location_in_tel"]},
                    {"type":"text","text":parameters_in_tel["price_in_tel"]},
                    {"type":"text","text":add_description},
                    {"type":"text","text":property_id}  
                    ]
        logger.debug(f"parameters_in_english:{params_in_english}")
        logger.debug(f"params_in_telugu:{params_in_telugu}")
        logger.debug(f"ph_numbers:{ph_numbers}")
        for ph_num_obj in ph_numbers:
            ph_num=ph_num_obj.get("ph_num")
            langauge=ph_num_obj.get("langauge")
            logger.debug(f"prefered_langauge:{langauge}")
            if langauge=="Telugu":
                send_property_card_in_telugu(property_id=property_id,img_url=prop_img, params_in_telugu=params_in_telugu,phone_num=ph_num)
            else:
                send_property_card_in_english(property_id=property_id,img_url=prop_img, params_in_english=params_in_english,phone_num=ph_num)
        tot_users=len(ph_numbers)
        logger.debug(f"property {property_id} is notified to {tot_users}")
        return {"total_users":tot_users,"action":True}
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    
def get_district_object(district_id,session):
    try:
        query=select(District).where(District.id==district_id)
        dist_obj=session.execute(query).scalar()
        return dist_obj
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e
    
def date_to_datetime_obj(date):
    formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d %H:%M:%S","%Y-%m-%d %H:%M:%S.%f"]
    for fmt in formats:
        try:
            return datetime.strptime(date, fmt)
        except ValueError:
            continue
    logger.error(f"Error converting date: {date} does not match any known format")
    raise ValueError(f"Date {date} does not match any known format")
    
    
def send_whatsapp_notifications_to_single_user(prop_obj,params,seller_number=None,interest=False,get_params=False):
    try:
        logger.debug(f"sending whatsap notification of property:{prop_obj}")
        district = prop_obj.district
        village = prop_obj.village
        property_type=prop_obj.p_type
        property_listing=prop_obj.listing_type
        area=prop_obj.size
        buy_price_range=prop_obj.doc_num
        units=prop_obj.unit
        prop_price=prop_obj.price
        bhk=prop_obj.bhk
        property_id=prop_obj.p_id
        logger.debug(f"district:{district}")
        logger.debug(f"area:{village}")
        logger.debug(f"property:{property_type}")
        if not (property_listing and village and district and property_type and units and area):
            logger.debug("required params not existed to send property notification")
            return {"total_users": 0, "action": False}
        elif property_listing=="sell":
            if not prop_price:
                logger.debug("property price not existed to sent notification")
                return {"total_users":0,"action":False}
        elif property_listing=="buy":
            if not buy_price_range:
                logger.debug("property price range not existed to sent notification")
                return {"total_users":0,"action":False}
            buy_price_val=buy_price_range.split("-")
            if len(buy_price_val)!=2:
                logger.debug("property price range not in required format to sent notification")
                return {"total_users":0,"action":False}
        prop_img = None
        for image_objs in prop_obj.all_prop_imgs:
            if image_objs:
                prop_img = image_objs.img_url
            break
        if prop_img:     #disucss this condition when it uploded to server
            res = prop_img.split(":")
            res[0] = "https"
            prop_img = res[0] + ":" + res[1]
            print(f"modified_prop_img:{prop_img}")
        if not prop_img:
            default_property_url=None
            if property_listing=="buy":
                default_property_url=DEFAULT_PROPERTY_URLS_FOR_WHATSAPP["buy"].get(property_type,None)
            else:    
                default_property_url=DEFAULT_PROPERTY_URLS_FOR_WHATSAPP["sell"].get(property_type,None)
            if not default_property_url:
                default_property_url=DEFAULT_PROPERTY_URLS_FOR_WHATSAPP.get("default")
            prop_img=default_property_url
        phone_nums_area_id={"ph_numbers":params.get("ph_num",None),"area_id":params.get("area_id",None)}
        logger.debug(f"phone_nums_area_id:{phone_nums_area_id}")
        ph_numbers=phone_nums_area_id["ph_numbers"]
        area_id=phone_nums_area_id["area_id"]
        logger.debug(f"area_id:{area_id} of {village}")
        parms_obj=get_parameters_for_property_card(area_id=area_id,area=area,property_type=property_type,listing_type=property_listing,bhk=bhk,village=village,price=prop_price,units=units,buy_price_range=buy_price_range)
        parameters_in_tel=parms_obj["parameters_in_tel"]
        parameters_in_eng=parms_obj["parameters_in_eng"]
        area_name_in_tel=parms_obj["area_name_in_tel"]
        property_id_to_sent=property_id
        if interest and seller_number:
            property_id_to_sent=str(property_id)+f",*Seller Number*:{seller_number}"
        if get_params:
            return parameters_in_eng
        logger.debug(f"parameters_in_tel:{parameters_in_tel}")
        logger.debug(f"parameters_in_eng:{parameters_in_eng}")
        logger.debug(f"area name in telugu:{area_name_in_tel}")
        add_description=get_add_description(area_name=village)
        if not add_description:
            add_description=random.choice(DEFAULT_ADS)
        params_in_english=[
                        {"type":"text","text":parameters_in_eng["location_in_eng"]},
                        {"type":"text","text":parameters_in_eng["price_in_eng"]},
                        {"type":"text","text":add_description},
                        {"type":"text","text":property_id_to_sent}  
                        ]
        params_in_telugu=[
                    {"type":"text","text":parameters_in_tel["location_in_tel"]},
                    {"type":"text","text":parameters_in_tel["price_in_tel"]},
                    {"type":"text","text":add_description},
                    {"type":"text","text":property_id_to_sent}
                    ]
        logger.debug(f"parameters_in_english:{params_in_english}")
        logger.debug(f"params_in_telugu:{params_in_telugu}")
        logger.debug(f"ph_numbers:{ph_numbers}")
        for ph_num_obj in ph_numbers:
            ph_num=ph_num_obj.get("ph_num")
            langauge=ph_num_obj.get("langauge")
            logger.debug(f"prefered_langauge:{langauge}")
            if langauge=="Telugu":
                send_property_card_in_telugu(property_id=property_id,img_url=prop_img, params_in_telugu=params_in_telugu,phone_num=ph_num)
            else:
                send_property_card_in_english(property_id=property_id,img_url=prop_img, params_in_english=params_in_english,phone_num=ph_num)
        tot_users=len(ph_numbers)
        logger.debug(f"property {property_id} is notified to {tot_users}")
        return {"total_users":tot_users,"action":True,"area_name_in_tel":area_name_in_tel}
    except SQLAlchemyError as e:
        raise e
    except Exception as e:
        raise e