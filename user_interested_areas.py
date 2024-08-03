from flask import request,Blueprint
from flask_restful import Api,Resource
import logging
import json
from sqlalchemy.exc import IntegrityError, SQLAlchemyError,NoResultFound
from session import get_session
from user_interested_areas_crud import add_selected_area,delete_user_interested_areas,get_all_existing_districts,get_entire_district_id,get_user_registered_areas,add_new_area_with_area_name,add_new_district_with_name
from crud import get_user_profile,read_json_file
user_interested_areas_bp=Blueprint("user_interested_areas",__name__)
logger=logging.getLogger(__name__)
api=Api(user_interested_areas_bp)


class RegisterInterestedAreas(Resource):
    def post(self):   #to add new area into data base
        try:
            logger.debug("adding new area into data base")
            data=request.json
            if not data:
                logger.warning("data not provided to add area")
                return {"status":"fail","message":"data not provided"},400
            logger.info(f"areas to add into data base:{data}")
            user_id=data.get("user_id",None)
            state=data.get("state",None)
            district=data.get("district",None)
            areas_data=data.get("areas",None)
            if not (user_id and state and district and areas_data):
                logger.warning("user_id , state , district and areas_data not provided to add new areas into to db")
                return {"status":"fail","messge":"provide user_id , state , district and areas_data to add areas"},400
            with get_session() as session:
                user_obj=get_user_profile(session=session,user_id=user_id)
                if not user_obj:
                    logger.warning(f"user {user_id} not exist to add area")
                    return {"status":"fail","message":"Un authorized access"},404
                if user_obj.role !="admin":
                    logger.warning("other than admin requested to add areas ")
                    return {"status":"fail","message":"Un authorized access"},404
                districts_exist_in_database=get_all_existing_districts(session=session)
                # areas_data=read_json_file(file_name)
                area_added=[]
                district_in_english=district.get("English",None)
                if not district_in_english:
                    return {"status":"fail","message":"plese provide district name in english"}
                data_to_add_in_files={}
                if district_in_english not in districts_exist_in_database:
                    add_new_district_with_name(session=session,state=state,district=district_in_english)
                    for langauge,district_name in district.items():
                        # langauge,district_name=district_name_obj.items()
                        if langauge=="English":
                            continue
                        file_name=f"areas_in_{langauge}"
                        if file_name in data_to_add_in_files:
                            data_to_add_in_files[file_name][district_in_english]=district_name
                        else:
                            data_to_add_in_files[file_name]={district_in_english:district_name}
                logger.debug(f"district names in different langauges:{data_to_add_in_files}")                 
                for area_obj in areas_data:
                    area_name_in_english=area_obj.get("English",None)
                    if not area_name_in_english:
                        logger.debug(f"no area name in english for area_obj:{area_obj}")
                        return {"status":"fail","message":f"please add area name in english for area_obj:{area_obj}"}
                    area_id=add_new_area_with_area_name(session=session,area_name=area_name_in_english,district_id=district_in_english)
                    logger.debug(f"area_id:{area_id}")
                    for langauge,value in area_obj.items():
                        if langauge=="English":
                            continue
                        file_name=f"areas_in_{langauge}"
                        if file_name in data_to_add_in_files:
                            data_to_add_in_files[file_name][str(area_id)]=value
                        else:
                            data_to_add_in_files[file_name]={str(area_id):value}
                session.commit()
                logger.debug(f"data to add in different files:{data_to_add_in_files}")
                for file_name in data_to_add_in_files:
                    formated_file=file_name+".json"   
                    logger.debug(f"formated file_name:{formated_file}")
                    old_data=read_json_file(file_name=formated_file)                      
                    res_areas_data=data_to_add_in_files[file_name]
                    old_data.update(res_areas_data)
                    logger.debug(f"data to update:{old_data}")
                    with open(formated_file, 'w', encoding='utf-8') as file:
                        json.dump(old_data, file, indent=4, ensure_ascii=False)
                    logger.debug(f"data updated successfullty to :{formated_file}")
            return {"status":"success","message":" areas added successfully","added areas":area_added},201

        except IntegrityError as se:
            logger.error(f"Integrity error while adding new area into db:{se.orig}")
            return {"status":"fail","message": "Area alredy exists"}, 400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while adding new area into db: {e}")
            return {"status":"fail","message": "server error"}, 400
        except Exception as e:
            logger.critical(f"unexpected error while adding new area into db:{e}")
            return {"status":"fail","message": "Internall Error"}, 500

    def get(self):
        try:
            logger.debug("getting user interested areas")
            data=request.args.to_dict()
            if not data:
                logger.warning("data not provided to get user intersted areas")
                return {"status":"fail","message":"data not provided"},400
            logger.info(f"data to get intersted areas:{data}")
            user_id=data.get("user_id",None)
            if not user_id:
                logger.warning(f"user_id not provided to get intersted areas")
                return {"status":"fail","messge":"user_id not provided"},400
            with get_session() as session:
                user_obj=get_user_profile(user_id=user_id,session=session)
                if not user_obj:
                    logger.warning(f"user {user_id} not exist to get their interested areas")
                    return {"status":"fail","message":"user not found"},400
                user_registered_areas=get_user_registered_areas(user_obj=user_obj)
                registered_areas=user_registered_areas['registered_areas']
                logger.debug(f"user {user_id} registered areas:{registered_areas}")
                return {"status":"success","interested_areas":registered_areas}
        except NoResultFound as e:
            logger.error(f"Error finding user {user_id}: {e}")
            return {"status":"fail","message":"user not found"},400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy errorgetiing intersterd areas: {e}")
            return {"status":"fail","message": f"Server Error"}, 400
        except Exception as e:
            logger.critical(f"unexpected error while getiing intersterd areas:{e}")
            return {"status":"fail","message": f"Internall Error"}, 500


    def put(self):
        try:
            logger.debug("adding intersted areas")
            data=request.json
            if not data:
                logger.warning("data not provided to update the user interested areas")
                return {"status":"fail","message":"data not provided"},400
            logger.info(f"data to add intersted areas:{data}")
            user_id=data.get("user_id",None)
            req_user_id=data.get("req_user_id",None)
            if not user_id or not req_user_id:
                logger.warning("user_id or requsted_user_id not provided to add intersted areas")
                return {"status":"fail","messge":"user_id not provided"},400
            areas_to_update=data.get("body",None)
            if not areas_to_update:
                logger.warning("areas_to_update not provided")
                return {"status":"fail","message":"areas_to_update not provided"},400
            with get_session() as session:
                user_obj=get_user_profile(session=session,user_id=user_id)
                if not user_obj:
                    logger.warning(f"user {user_id} not found to add intersted areas")
                    return {"status":"fail","message":"Un authorized access"},404
                if user_id!=req_user_id:
                    requsted_user_obj=get_user_profile(session=session,user_id=req_user_id)
                    if not requsted_user_obj:
                        logger.warning(f"requsted user {req_user_id} did not exist")
                        return {"status":"fail","message":"Un Authorized Access"},404
                    if requsted_user_obj.role not in ["staff","admin"]:
                        logger.warning(f"other than admin {req_user_id} requsted to add intersted areas on behalf of user {user_id}")
                for obj in areas_to_update:
                   area_ids=obj.get("areas",None)
                   status=obj.get("status",None)
                   district=obj.get("district",None)
                   if not status :
                       logger.warning(f"status not provided to update intersted areas")
                       return {"status":"fail","message":"please provide intersted status"},400
                   if status=="delete":
                        for area_id in area_ids:
                                delete_user_interested_areas(session=session,user_id=user_id,area_id=area_id)
                   elif status=="add":
                        if not district:
                            logger.warning(f"district not provided to add intersted areas")
                            return {"status":"fail","message":"district not provided"},400
                        entire_district_id=get_entire_district_id(session=session,district_id=district)
                        user_registered_areas=get_user_registered_areas(user_obj=user_obj)
                        user_registered_area_ids=user_registered_areas["registered_area_ids"]
                        logger.debug(f"entire district id:{entire_district_id}")
                        logger.debug(f"area_ids to add:{area_ids}")
                        if entire_district_id in user_registered_area_ids:
                            continue
                        elif entire_district_id in area_ids:
                            logger.debug("adding entire district")
                            add_selected_area(session=session,area_id=entire_district_id,user_id=user_id,district_id=district,action=True)
                        else:
                            for area_id in area_ids:
                                if area_id in user_registered_area_ids:
                                    continue
                                else:
                                    add_selected_area(session=session,area_id=area_id,user_id=user_id,district_id=district,action=False)
                user_registered_areas=get_user_registered_areas(user_obj=user_obj)
                logger.debug(f"user_registered_areas:{user_registered_areas['registered_areas']}")
                logger.info("areas addded successfully")
                return {"status":"success","message":"areas updated successfully","interested_areas":user_registered_areas["registered_areas"]},201
        except IntegrityError as se:
            logger.error(f"Integrity error while updating intersterd areas:{se.orig}")
            return {"status":"fail","message": "area alredy Exists"}, 400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy errorupdating intersterd areas: {e}")
            return {"status":"fail","message": f"Server Error"}, 400
        except Exception as e:
            logger.critical(f"unexpected error while updating intersterd areas:{e}")
            return {"status":"fail","message": "Internall Error"}, 500
        
api.add_resource(RegisterInterestedAreas,'/register')

