from flask import Blueprint, request, current_app, jsonify
from global_varibles import IMAZE_SIZE
import mimetypes
import datetime
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import os
import logging
from PIL import Image
from io import BytesIO
from sqlalchemy import text
from session import get_session
from models import Property_img
from crud import get_user_profile, get_property_object,update_property, get_image_object, delete_property_img,add_property_documents,individual_property_details

prop_img_bp = Blueprint("property_images",
                        __name__,
                        static_folder="files",
                        template_folder="templates",
                        static_url_path='/files')

logger=logging.getLogger(__name__)
api = Api(prop_img_bp)


class Property_image(Resource):
    def post(self):
        try:
            logger.info("adding property image or document")
            data=request.form.to_dict()
            if not data:
                logger.warning("data not provided to add the property image or document")
                return {"status":"fail","message":"plese provide data"},400     
            logger.info(f"property image data to add: {data}")
            req_user_id = data.get('req_user_id', None)
            user_id = data.get('user_id', None)
            property_id = data.get("p_id", None)
            img_status=data.get("status","not verified")
            if not req_user_id or not user_id or not property_id:
                logger.warning("req user or user_id not provided to add image")
                return {"status":"fail","message": "Please provide user_id , request_id and property_id"}, 400
            images =[]
            documents=[]
            if request.files:
                images=request.files.getlist("images") 
                documents=request.files.getlist("documents") 
            logger.debug(f"images to add:{images}")
            logger.debug(f"documents to add:{documents}")
            allowed_extensions = {
                'image/jpg', 'image/gif', 'image/jpeg', 'image/png'
            }
            allowed_doc_extensions=[
                "application/pdf","application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                     ]
            max_file_size = IMAZE_SIZE
            errors = []
            # image_ids={}
            with get_session() as session:
                is_admin = False
                if user_id != req_user_id:
                    req_user_obj = get_user_profile(req_user_id, session)
                    if not req_user_obj:
                        logger.warning(f"requseted user {req_user_id} profile to add image is not exists")
                        return {"status": "fail", "message": 'Unauthorized Access'}, 401
                    if req_user_obj.role not in ['admin',"staff"]:
                        logger.warning(f"Requested user {user_id} to add property image or document was not a admin or not a staff")
                        return {"status": "fail", "message": 'Unauthorized request'}, 401
                    is_admin = True
                prop_obj = get_property_object(property_id, session)
                if not prop_obj:
                    logger.warning(f"property {property_id} not in exist")
                    return {"status": "fail", "message": "Property not availble"}, 401
                logger.debug(f"property details:{prop_obj}")
                if prop_obj.cont_user_id != user_id:
                    logger.warning(f"user {user_id} not belongs to the requsted property {prop_obj.p_id}")
                    return {"status": "fail", "message": "Un Authorized"}, 401
                session.execute(text("PRAGMA foreign_keys = ON;"))
                property_id=prop_obj.p_id
                doc_urls=""
                if is_admin and  len(documents)>0:
                    documents=list(set(documents))
                    property_type=prop_obj.p_type
                    document_number=prop_obj.doc_num
                    mediator_number=prop_obj.med_num1
                    property_location=prop_obj.village
                    response=add_property_documents(documents=documents,allowed_extensions=allowed_doc_extensions
                                                    ,property_id=property_id,property_type=property_type
                                                    ,document_number=document_number,mediator_number=mediator_number,
                                                    property_location=property_location)
                    logger.debug(f"response after adding the property:{response}")
                    doc_urls=response["res_urls_string"]
                    errors=response["errors"]
                    doc_files=prop_obj.docFile
                    if doc_files and doc_urls !="":
                        doc_files=doc_files+","+doc_urls
                    elif doc_urls !="":
                        doc_files=doc_urls
                    else:
                        pass
                    data_to_update={"docFile":doc_files}
                    update_property(property_id=property_id, data_to_update=data_to_update,
                                                session=session)
                    logger.debug("documents addeed successfully")
                
                images=list(set(images))
                for image in images:
                    file_name = secure_filename(image.filename)
                    image_type = mimetypes.guess_type(file_name)
                    logger.debug(f"img_type:{image_type[0]}")
                    if image_type[0] not in allowed_extensions :
                        logger.debug({"Not a vaild file type"})
                        errors.append(f"Invalid File Type :{file_name}")
                        continue
                    file_data = image.read()
                    if len(file_data) > max_file_size:
                        logger.error({f"file size exceeded for {file_name}"})
                        errors.append(f"file size exceeds:{file_name}")
                        continue
                    logger.debug(f"img_size:{len(file_data)}")
                    logger.debug(f'File Name : {file_name}')
                    folder_name = current_app.config['UPLOAD_FOLDER']
                    folder_name+="/images"
                    current_datetime = datetime.datetime.now()
                    datetime_str = current_datetime.strftime("%Y_%m_%d_%H_%M_%S")
                    name, ext = file_name.rsplit('.', 1)
                    file_name = f"{name}_{datetime_str}.{ext}"
                    absolute_path = os.path.join(folder_name, file_name)
                    logger.debug(f"abs_path: {absolute_path}")
                    image = Image.open(BytesIO(file_data))
                    image.save(absolute_path)
                    base_url = request.url_root
                    relative_path = os.path.relpath(absolute_path, folder_name)
                    logger.debug(f"reltive_pathe:{relative_path }")
                    image_url = os.path.join(base_url, 'files/images', relative_path)
                    logger.debug(f"image_url: {image_url}")
                    data = {
                        "prop_id": property_id,
                        "img_url": image_url,
                        "status": img_status
                    }
                    query_to_add_img=Property_img(**data)
                    session.add(query_to_add_img)
                    session.commit()
                    logger.debug("individual image added successfully")
                if len(images)>0 and not is_admin and prop_obj.v_status:
                    logger.debug("updating the status of property")
                    data_to_update={"v_status":False}
                    update_property(property_id=property_id, data_to_update=data_to_update,
                                                session=session)
                property_details=individual_property_details(property_obj=prop_obj,is_admin=False)
                logger.debug("All images/documents added successfully")
                logger.debug(f"image/documents uploading errors:{errors}")
                if errors:
                    raise ValueError(errors)
                return {
                    "status": "success",
                    "message": "Images added successfully",
                    "details":property_details
                    # "image_ids":image_ids
                }, 201
        except ValueError as ve:
            logger.warning(f"value errors while uploding images:{ve}")
            return {"status":"fail","message":str(ve)},400
        except IntegrityError as se:
            logger.error(f"Integrity error while uploding images: {se.orig}")
            return {"status":"fail","message":se},400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while uploding images: {e}") 
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while uploding images: {e}")
            return {"status":"fail","message":"Internall Error"},500

    def get(self):
        try:
            logger.debug("getting  property images")
            data = request.form.to_dict()
            logger.info(f"image request params:{data}")
            req_user_id = data.get('req_user_id', None)
            user_id = data.get('user_id', None)
            img_id = data.get("img_id", None)
            if not req_user_id or not user_id or not img_id:
                logger.warning("req user or user id not provided to add image")
                return {"status":"fail","message": "Please provide user_id , request_id and img_id"}, 400
            with get_session() as session:
                if user_id != req_user_id:
                    req_user_obj = get_user_profile(req_user_id, session)
                    if not req_user_obj:
                        logger.warning("requested user to add image dis not have a account")
                        return {"status": "fail","message": 'Unauthorized Access'}, 401
                    elif req_user_obj.role not in ['admin',"staff"]:
                        logger.warning("unkown person requsted to get property image")
                        return {"status": "fail","message": 'Unauthorized request'}, 401
                img_obj = get_image_object(img_id, session)
                if not img_obj:
                    logger.warning(f"requsted image not existed")
                    return {
                        "status": "fail",
                        "message": "Image not exsited"
                    }, 401
                property_obj = get_property_object(img_obj.prop_id,
                                                    session)
                logger.debug(f"property object:{property_obj}")
                if not property_obj:
                    logger.warning(f"property {img_obj.prop_id} not exists")
                    return {"status":"fail","message":"Un Authorized Access"},404
                if property_obj.cont_user_id != user_id:  
                    logger.warning(f"property not belongs to {user_id}")
                    return {
                        "status": "fail",
                        "message": "Un Authorized"
                    }, 401
                data_dict = dict(img_obj)
                logger.info(f"image data:{data_dict}")
                return jsonify({
                    "status": 'success',
                    "profile": {
                        **(data_dict)
                    }
                }),200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while getting images: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while getting images: {e}")
            return {"status":"fail","message":"Internall Error"},500

    def delete(self):
        try:
            logger.debug("deleting the property images")
            data=request.json
            if not data:
                logger.warning("data not provided to delete the images")
                return {"status":"fail","message":"data not provided"},400
            logger.info(f"data to delete the image:{data}")
            req_user_id=data.get("req_user_id",None)
            user_id=data.get("user_id",None)
            # img_id=data.get("img_id",None)
            img_ids=data.get("img_ids",None)
            if not req_user_id or not user_id or not img_ids:
                logger.warning("required params not provided to delete the image")
                return {"status":"fail","message":"req_user_id or user_id or img_id not provided"},400
            with get_session() as session:
                if user_id != req_user_id: 
                    req_user_obj = get_user_profile(req_user_id, session)
                    if not req_user_obj:
                        logger.warning(f"requsted user {req_user_id} did not have profile")
                        return {"status": "fail","message": 'Unauthorized Access'}, 401
                    if req_user_obj.role not in ['admin','staff']:
                        logger.warning(f"other than adminstrtor  with id {req_user_id} requsted to delete the property image")
                        return {
                            "status": "fail",
                            "message": 'Unauthorized request'
                        }, 401
                property_obj=None
                for img_id in img_ids:
                    img_obj = get_image_object(img_id, session)
                    if not img_obj:
                        logger.warning(f"image with id :{img_id} is not availble to delete")
                        return {
                            "status": "fail",
                            "message": "Un Authorized access"
                        }, 401
                    property_obj = get_property_object(img_obj.prop_id,
                                                        session)
                    logger.debug(f"property object:{property_obj}")
                    if not property_obj:
                        logger.warning(f"property {img_obj.prop_id} not exists")
                        return {"status":"fail","message":"Un Authorized Access"},404
                    if property_obj.cont_user_id != user_id:
                        # logger.info(f"contact_user:{property_obj.cont_user_id}")
                        logger.warning(f"property  not belongs to the user {user_id}")
                        return {
                            "status": "fail",
                            "message": "Un Authorized"
                        }, 401
                    image_url = img_obj.img_url
                    file_name = os.path.basename(image_url)
                    if image_url:
                        logger.debug(f"deleting:{file_name}")
                        folder_name = current_app.config['UPLOAD_FOLDER']
                        folder_name+="/images"
                        os.remove(os.path.join(folder_name, file_name))
                        logger.debug("Image deleted successfully", 201)
                        delete_property_img(img_id, session)
                    # return delete_property_img(img_id, session)
                property_details=individual_property_details(property_obj=property_obj,is_admin=False)
                logger.info("images deleted successfully")
                return {"status":"success","message":"images deleted successfully","details":property_details},200
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while deleting images: {e}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"unexpected error while deleting images: {e}")
            return {"status":"fail","message":"Internall Error"},500
        


api.add_resource(Property_image, '/image')

