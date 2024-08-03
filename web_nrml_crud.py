
from sqlalchemy.exc import  SQLAlchemyError
from session import get_session
import logging
import time
from crud import read_json_file,get_user_profile_for_whatsapp_users
from user_interested_areas_crud import get_district_id

areas_in_telugu="areas_in_Telugu.json"
supporting_areas="areas_supporting.json"

logger=logging.getLogger(__name__)




def get_areas_for_selected_districts(selected_districts,telugu,is_plan_active=False):
    try:
        logger.debug("sending areas for selcted districts")
        mandals_to_pass=[]
        supporting_areas_json=read_json_file(file_name=supporting_areas)
        if telugu:
            json_data=read_json_file(file_name=areas_in_telugu)
        for district in supporting_areas_json["areas"]:
            if district in selected_districts:
                for area_obj in supporting_areas_json["areas"][district]:
                    area_id=area_obj["id"]
                    area_name=area_obj["area"]
                    area_id=str(area_id)
                    if telugu:
                        district_name_in_telugu=json_data.get(district,None)
                        if not district_name_in_telugu:
                            district_name_in_telugu=district
                        if area_name=="All Areas":
                            if is_plan_active:
                                mandals_to_pass.append({"id":area_id,"title":f"అన్ని {district_name_in_telugu} ప్రాంతాలు"})
                            else:
                                mandals_to_pass.append({"id":area_id,"title":f"అన్ని {district_name_in_telugu} ప్రాంతాలు",'enabled': False})
                        else:
                            area_name_in_telugu=json_data.get(area_id,None)  
                            if not area_name_in_telugu:
                                area_name_in_telugu=area_name                                      
                            mandals_to_pass.append({"id":area_id,"title":area_name_in_telugu})
                    else:
                        if area_name=="All Areas":
                            if is_plan_active:
                                mandals_to_pass.append({"id":area_id,"title":f"All {district} Areas"})
                            else:
                                mandals_to_pass.append({"id":area_id,"title":f"All {district} Areas",'enabled': False})
                        else:
                            mandals_to_pass.append({"id":area_id,"title":area_name})
        logger.debug(f"mandals to pass  for selcted districts:{mandals_to_pass}")
        return mandals_to_pass
    except Exception as e:
        logger.critical(f"faile to areas for selected districts:{e}")
        raise e

def get_districts_from_file(selected_states,telugu):
    try:
        logger.debug(f"sending districts for {selected_states}")
        districs_to_send = []
        supporting_areas_json=read_json_file(file_name=supporting_areas)
        if telugu:
            json_data=read_json_file(file_name=areas_in_telugu)
            for state in supporting_areas_json["district_status"]:
                if state in selected_states:
                    for district,status in supporting_areas_json["district_status"][state].items():
                        if status:
                            name_in_telugu=json_data.get(district,None)
                            if not name_in_telugu:
                                name_in_telugu=district
                            districs_to_send.append({"id":district,"title":name_in_telugu})
            districs_to_send=sorted(districs_to_send,key=lambda x:x["id"])
        else:
            for state in supporting_areas_json["district_status"]:
                if state in selected_states:
                    for district,status in supporting_areas_json["district_status"][state].items():
                        if status:
                            districs_to_send.append({"id":district,"title":district})
            districs_to_send=sorted(districs_to_send,key=lambda x:x["title"])
        return districs_to_send
    except Exception as e:
        logger.critical(f"faile to send districts for selected states:{e}")
        raise e

def get_selected_states(user_obj):
    try:
        logger.debug("getting user selected states")
        selected_states=[]
        for state_obj in user_obj.states:
            state_name=state_obj.id
            selected_states.append(state_name) 
        logger.debug(f"selected_states:{selected_states}")
        return selected_states
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while getting user selected states:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send selected states:{e}")
        raise e

def get_selected_districts(user_obj,telugu=False):
    try:
        logger.debug("getting user selected districts")
        
        selected_districts=[]
        selected_districts_exmp=[]
        if telugu:
            json_data=read_json_file(areas_in_telugu) 
            for district_object in user_obj.districts:
                district_name=district_object.name
                logger.debug(f"district_name:{district_name}")
                selected_districts.append(district_name)
                name_in_telugu=json_data.get(district_name,district_name)
                logger.debug(f"selected_districts:{selected_districts}")
                selected_districts_exmp.append({"id":district_name,"title":name_in_telugu})
            selected_districts_exmp=sorted(selected_districts_exmp,key=lambda x:x["id"])
        else:
            for district_object in user_obj.districts:
                district_name=district_object.name
                logger.debug(f"district_name:{district_name}")
                selected_districts.append(district_name) 
                logger.debug(f"selected_districts:{selected_districts}")
                selected_districts_exmp.append({"id":district_name,"title":district_name})
            selected_districts_exmp=sorted(selected_districts_exmp,key=lambda x:x["title"])
        return {"selected_districts":selected_districts,"selected_districts_exmp":selected_districts_exmp}
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while getting user selected districts:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send selected districts:{e}")
        raise e

def get_user_selected_areas(user_obj):
    try:
        logger.debug("getting user selectred areas")
        selected_areas=[]
        for area_obj in user_obj.areas:
            selected_areas.append(str(area_obj.id))
        return selected_areas
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while getting user selected areas:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send selected areas:{e}")
        raise e
def get_selected_areas(user_obj,telugu=False):
    try:
        logger.debug("getting user selected areas")
        selected_areas=[]
        selected_area_exmp=[]
        active_notifications=user_obj.active_notifications
        if telugu:
            json_data_in_telugu=read_json_file(areas_in_telugu) 
            for area_object in user_obj.areas:
                area_id=str(area_object.id)
                area_name=area_object.name
                area_name_in_telugu=json_data_in_telugu.get(area_id,area_name)
                selected_areas.append(area_id)
                if area_name=="All Areas":
                    district_name_in_telugu=json_data_in_telugu.get(area_object.district_id,area_object.district_id)
                    if active_notifications>0:
                        selected_area_exmp.append({"id":area_id,"title":f"అన్ని {district_name_in_telugu} ప్రాంతాలు"})

                    else:
                        selected_area_exmp.append({"id":area_id,"title":f"అన్ని {district_name_in_telugu} ప్రాంతాలు",'enabled': False})

                else:
                    selected_area_exmp.append({"id":area_id,"title":area_name_in_telugu})
            # selected_area_exmp=sorted(selected_area_exmp,key=lambda x:x["title"])
        else:
            for area_object in user_obj.areas:
                area_name=area_object.name
                area_id=str(area_object.id)
                selected_areas.append(area_id)
                if area_name=="All Areas":
                    if active_notifications>0:
                        selected_area_exmp.append({"id":area_id,"title":f"All {area_object.district_id} Areas"})
                    else:
                        selected_area_exmp.append({"id":area_id,"title":f"All {area_object.district_id} Areas",'enabled': False})
                else:
                    selected_area_exmp.append({"id":area_id,"title":area_name})
            selected_area_exmp=sorted(selected_area_exmp,key=lambda x:x["title"])                
        logger.debug(f"selected_areas:{selected_areas},selected areas:{selected_area_exmp}")
        return {"selected_areas":selected_areas,"selected_area_exmp":selected_area_exmp}
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while getting user selected areas:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send selected areas:{e}")
        raise e


def get_state_response(user_obj,version,telugu):
    try:
        logger.debug("sending state response")
        logger.debug(f"sending state response to:{user_obj}")
        selected_states=get_selected_states(user_obj)
        state_to_send=[]
        supporting_areas_json=read_json_file(supporting_areas)
        if telugu:
            telugu_json_data=read_json_file(file_name=areas_in_telugu)
            states=supporting_areas_json.get("state_status")
            for state_obj in states:
                state=state_obj["state"]
                status=state_obj["status"]
                if status:
                    name_in_telugu=telugu_json_data.get(state,None)
                    if not name_in_telugu:
                        name_in_telugu=state
                    state_to_send.append({"id":state,"title":name_in_telugu})
            state_to_send=sorted(state_to_send,key=lambda x:x["id"])
        else:
            states=supporting_areas_json.get("state_status")
            for state_obj in states:
                state=state_obj["state"]
                status=state_obj["status"]
                if status:
                    state_to_send.append({"id":state,"title":state})
            state_to_send=sorted(state_to_send,key=lambda x:x["title"])
        response = {
            "version": version,
            "screen": "choose_interested_states",
            "data": {
                "selected_state_1": state_to_send[:20],
                # "selected_state_2": state_data["state"][2:],
                "user_existence":1,  #true
                # "select_areas":mandals_to_pass,
                "init_states":{
                    "selected_state_1": selected_states
                    # "select_areas":selected_areas
                }
            }
        }
        logger.debug(f"state response:{response}")
        return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while getting state response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send state response:{e}")
        raise e

def get_state_response_1(user_obj,version,telugu):
    try:
        logger.debug(f"sending state response to:{user_obj}")
        selected_states=get_selected_states(user_obj)
        state_to_send=[]
        supporting_areas_json=read_json_file(supporting_areas)
        if telugu:
            json_data=read_json_file(file_name=areas_in_telugu)
            states=supporting_areas_json.get("state_status")
            for state_obj in states:
                state=state_obj["state"]
                status=state_obj["status"]
                if status:
                    name_in_telugu=json_data.get(state,None)
                    if not name_in_telugu:
                        name_in_telugu=state
                    state_to_send.append({"id":state,"title":name_in_telugu})
            state_to_send=sorted(state_to_send,key=lambda x:x["id"])

        else:
            states=supporting_areas_json.get("state_status")
            for state_obj in states:
                state=state_obj["state"]
                status=state_obj["status"]
                if status:
                    state_to_send.append({"id":state,"title":state})
            state_to_send=sorted(state_to_send,key=lambda x:x["title"])
        response = {
            "version": version,
            "screen": "choose_interested_states_rentry",
            "data": {
                "selected_state_1": state_to_send[:20],
                # "selected_state_2": state_data["state"][2:],
                "user_existence":1,  #true
                # "select_areas":mandals_to_pass,
                "init_states":{
                    "selected_state_1": selected_states
                    # "select_areas":selected_areas
                }
            }
        }
        logger.debug(f"state response:{response}")
        return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending state response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send state response:{e}")
        raise e

def get_init_res(ph_num,version,telugu,user_existence):
    try:
        logger.debug("sending states")
        with get_session() as session:
            if user_existence==1:
                user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
                response=get_state_response(user_obj=user_obj,version=version,telugu=telugu)
            else:
                state_to_send=[]
                supporting_areas_json=read_json_file(supporting_areas)
                if telugu:
                    json_data=read_json_file(file_name=areas_in_telugu)
                    states=supporting_areas_json.get("state_status")
                    for state_obj in states:
                        state=state_obj["state"]
                        status=state_obj["status"]
                        if status:
                            name_in_telugu=json_data.get(state,None)
                            if not name_in_telugu:
                                name_in_telugu=state
                            state_to_send.append({"id":state,"title":name_in_telugu})
                    state_to_send=sorted(state_to_send,key=lambda x:x["id"])
                else:
                    states=supporting_areas_json.get("state_status")
                    for state_obj in states:
                        state=state_obj["state"]
                        status=state_obj["status"]
                        if status:
                            state_to_send.append({"id":state,"title":state})
                    state_to_send=sorted(state_to_send,key=lambda x:x["title"])
                response = {
                    "version": version,
                    "screen": "choose_interested_states",
                    "data": {
                        "selected_state_1": state_to_send[:20],
                        # "selected_state_2": state_data["state"][20:],
                        "user_existence":0,
                        "init_states":{
                            "selected_state_1": []
                        }
                    }
                }
            logger.debug(f"init response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending init response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send init response:{e}")
        raise e
def get_init_res_1(ph_num,version,telugu,user_existence):
    try:
        logger.debug("sending init response")
        with get_session() as session:
            if user_existence==1:
                user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
                response=get_state_response_1(user_obj=user_obj,version=version,telugu=telugu)
            else:
                supporting_areas_json=read_json_file(supporting_areas)
                state_to_send=[]
                if telugu:
                    json_data=read_json_file(file_name=areas_in_telugu)

                    states=supporting_areas_json.get("state_status")
                    for state_obj in states:
                        state=state_obj["state"]
                        status=state_obj["status"]
                        if status:
                            name_in_telugu=json_data.get(state,None)
                            if not name_in_telugu:
                                name_in_telugu=state
                            state_to_send.append({"id":state,"title":name_in_telugu})
                    state_to_send=sorted(state_to_send,key=lambda x:x["id"])
                else:
                    states=supporting_areas_json.get("state_status")
                    for state_obj in states:
                        state=state_obj["state"]
                        status=state_obj["status"]
                        if status:
                            state_to_send.append({"id":state,"title":state})
                    state_to_send=sorted(state_to_send,key=lambda x:x["title"])
                response = {
                    "version": version,
                    "screen": "choose_interested_states_rentry",
                    "data": {
                        "selected_state_1": state_to_send[:20],
                        "user_existence":0,
                        "init_states":{
                            "selected_state_1": []
                        }
                    }
                }
            logger.debug(f"init response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending init response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send init response:{e}")
        raise e


def distribute_strings(data):
    try:
        logger.debug("distrubuting the data")
        lists = [[] for _ in range(5)]

        total_strings = len(data)
        logger.debug(f"total length of the data to distrubute: {total_strings}")

        base_count = total_strings // 5
        extra_count = total_strings % 5  
        index = 0
        for i in range(5):

            for _ in range(base_count):
                lists[i].append(data[index])
                index += 1

            if extra_count > 0:
                lists[i].append(data[index])
                index += 1
                extra_count -= 1


        for i in range(5):
            if not lists[i]: 
                lists[i].extend(lists[0])
        logger.debug(f"distrubuted data: {lists}")
        return lists
    except Exception as e:
        logger.critical(f"failed to distrubute the data into equall parts:{e}")
        raise e



def distribute_strings_into_two_pages(data):
    try:
        logger.debug("distrubuting the data into teo pages")
        lists = [[] for _ in range(2)]
        total_strings = len(data)
        logger.debug(f"total length of the data to distrubute: {total_strings}")
        base_count = total_strings // 2
        extra_count = total_strings % 2  
        index = 0
        for i in range(2):
            for _ in range(base_count):
                lists[i].append(data[index])
                index += 1
            if extra_count > 0:
                lists[i].append(data[index])
                index += 1
                extra_count -= 1
        logger.debug(f"distrubuted data:{lists}")
        return lists
    except Exception as e:
        logger.critical(f"failed to distrubte the data into two pages:{e}")
        raise e

def get_district_response(selected_states,version,ph_num,telugu):
    try:
        logger.debug("sending district response")
        with get_session() as session:
            user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
            user_selected_districts=get_selected_districts(user_obj,telugu=telugu)
            districs_to_send = get_districts_from_file(selected_states=selected_states,telugu=telugu)
            selected_districts_exmp=user_selected_districts["selected_districts_exmp"]
            for dict_entry in selected_districts_exmp:
                logger.debug(f"dic:{dict_entry}")
                if dict_entry in districs_to_send:
                    districs_to_send.remove(dict_entry)
                districs_to_send.insert(0,dict_entry)
                logger.debug(f"districs_to_send:{districs_to_send[0]}")
            logger.debug(f"selected_districts_exmp:{selected_districts_exmp}")
            logger.debug(f"checking the lenth of the elements")
            if len(districs_to_send) > 40:
                district_len = 41
                data_lists = distribute_strings_into_two_pages(data=districs_to_send[:40])
            else:
                district_len = len(districs_to_send)
                data_lists = distribute_strings_into_two_pages(data=districs_to_send)
            logger.debug(f"district_len:{district_len}")
            logger.debug(f"data_lists:{data_lists[0]}")
            selected_district_1=[]
            selected_district_2=[]
            for dict_entry in selected_districts_exmp:
                if dict_entry in data_lists[0]:
                    selected_district_1.append(dict_entry["id"])
                else:
                    selected_district_2.append(dict_entry["id"])
            response = {
                "version": version,
                "screen": "choose_interested_districts",
                "data": {
                    "selected_district_1": data_lists[0],
                    "selected_district_2": data_lists[1],
                    "states": selected_states,
                    "district_len": district_len,
                    "alr_selected_districts":[],
                    "user_existence":1,
                    "init_district": {
                        "selected_district_1": selected_district_1,
                        "selected_district_2":selected_district_2
                    }
                }
            }
            logger.debug(f"district response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending district response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send district response:{e}")
        raise e



def sending_districts_first_screen(selected_states,version,screen,user_existence,ph_num,telugu):
    try:
        logger.debug(f"screen:{screen}")
        if selected_states:
            if user_existence==1:
                response=get_district_response(selected_states,version,ph_num,telugu=telugu)
            else:
                supporting_areas_json=read_json_file(file_name=supporting_areas)
                districs_to_send = []
                if telugu:
                    json_data=read_json_file(file_name=areas_in_telugu)
                    for district in supporting_areas_json["areas"]:
                        name_in_telugu=json_data.get(district,None)
                        if not name_in_telugu:
                            name_in_telugu=district
                        districs_to_send.append({"id":district,"title":name_in_telugu})
                    districs_to_send=sorted(districs_to_send,key=lambda x:x["id"])
                else:
                    for district in supporting_areas_json["areas"]:
                        districs_to_send.append({"id":district,"title":district})
                    districs_to_send=sorted(districs_to_send,key=lambda x:x["title"])
                logger.debug(f"districts:{districs_to_send[0]}")

                if len(districs_to_send) > 40:
                    district_len = 41
                    data_lists = distribute_strings_into_two_pages(data=districs_to_send[:40])
                else:
                    district_len = len(districs_to_send)
                    data_lists = distribute_strings_into_two_pages(data=districs_to_send)
                logger.debug(f"district_len:{district_len}")
                logger.debug(f"data_lists:{data_lists[0]}")
                response = {
                    "version": version,
                    "screen": "choose_interested_districts",
                    "data": {
                        "selected_district_1": data_lists[0],
                        "selected_district_2": data_lists[1],
                        "states": selected_states,
                        "district_len": district_len,
                        "alr_selected_districts":[],
                        "user_existence":0,
                        "init_district": {
                            "selected_district_1": [],
                            "selected_district_2":[]
                        }
                    }
                }
            logger.debug(f"district respone:{response}")
            return response
        else:
            if screen=="choose_interested_states_rentry":
                response =get_init_res_1(ph_num=ph_num,version=version,telugu=telugu,user_existence=user_existence)
                return response
            else:
                response=get_init_res(ph_num=ph_num,version=version,telugu=telugu,user_existence=user_existence)
            logger.debug(f"district respone:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending district response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send district response:{e}")
        raise e


def get_district_response_1(selected_states,version,ph_num,al_selected_dists,telugu):
    try:
        logger.debug("sending district response to second district screen")
        with get_session() as session:
            user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
            user_selected_districts=get_selected_districts(user_obj,telugu=telugu)
            districs_to_send = get_districts_from_file(selected_states=selected_states,telugu=telugu)
            selected_districts_exmp=user_selected_districts["selected_districts_exmp"]
            for dict_entry in selected_districts_exmp:
                if dict_entry in districs_to_send:
                    districs_to_send.remove(dict_entry)
                districs_to_send.insert(0,dict_entry)
            logger.debug(f"selected_districts_exmp:{selected_districts_exmp}")
            logger.debug(f"checking the lenth of the elements")
            if len(districs_to_send) > 140:
                district_len = 141
                data_lists = distribute_strings(data=districs_to_send[40:140])
            else:
                district_len = len(districs_to_send)
                data_lists = distribute_strings(data=districs_to_send[40:])
            logger.debug(f"district_len:{district_len}")
            logger.debug(f"data_lists:{data_lists[0]}")
            init_values={
                "selected_district_1":[],
                "selected_district_2":[],
                "selected_district_3":[],
                "selected_district_4":[],
                "selected_district_5":[]
            }
            length_of_selected_districts=len(selected_districts_exmp)
            if length_of_selected_districts>40:
                for dict_entry in selected_districts_exmp:
                    if dict_entry in data_lists[0]:
                        init_values["selected_district_1"].append(dict_entry["id"])
                    elif dict_entry in data_lists[1]:
                        init_values["selected_district_2"].append(dict_entry["id"])
                    elif dict_entry in data_lists[2]:
                        init_values["selected_district_3"].append(dict_entry["id"])
                    elif dict_entry in data_lists[3]:
                        init_values["selected_district_4"].append(dict_entry["id"])
                    else:
                        init_values["selected_district_5"].append(dict_entry["id"])
            response = {
                "version": version,
                "screen": "choose_interested_districts_two",
                "data": {
                    "selected_district_1": data_lists[0],
                    "selected_district_2": data_lists[1],
                    "selected_district_3": data_lists[2],
                    "selected_district_4": data_lists[3],
                    "selected_district_5": data_lists[4],
                    "states": selected_states,
                    "district_len": district_len,
                    "alr_selected_districts":al_selected_dists,
                    "user_existence":1,
                    "init_district": init_values
                }
            }
            logger.debug(f"district response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending district response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send district response:{e}")
        raise e

def get_district_response_2(selected_states,version,ph_num,al_selected_dists,telugu):
    try:
        logger.debug("sending district response")
        with get_session() as session:
            user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
            # district_data=json.loads(read_file(districts_file))
            districs_to_send = get_districts_from_file(selected_states=selected_states,telugu=telugu) 
            user_selected_districts=get_selected_districts(user_obj,telugu=telugu)
            selected_districts_exmp=user_selected_districts["selected_districts_exmp"]
            for dict_entry in selected_districts_exmp:
                if dict_entry not in districs_to_send:
                    districs_to_send.remove(dict_entry)
                districs_to_send.insert(0,dict_entry)
            logger.debug(f"selected_districts_exmp:{selected_districts_exmp}")
            logger.debug(f"checking the lenth of the elements")
            district_len=len(districs_to_send)
            data_lists=distribute_strings(data=districs_to_send[140:240])
            logger.debug(f"district_len:{district_len}")
            logger.debug(f"data_lists:{data_lists[0]}")
            init_values={
                "selected_district_1":[],
                "selected_district_2":[],
                "selected_district_3":[],
                "selected_district_4":[],
                "selected_district_5":[]
            }
            length_of_selected_districts=len(selected_districts_exmp)
            if length_of_selected_districts>140:
                for dict_entry in selected_districts_exmp:
                    if dict_entry in data_lists[0]:
                        init_values["selected_district_1"].append(dict_entry["id"])
                    elif dict_entry in data_lists[1]:
                        init_values["selected_district_2"].append(dict_entry["id"])
                    elif dict_entry in data_lists[2]:
                        init_values["selected_district_3"].append(dict_entry["id"])
                    elif dict_entry in data_lists[3]:
                        init_values["selected_district_4"].append(dict_entry["id"])
                    else:
                        init_values["selected_district_5"].append(dict_entry["id"])
            response = {
                "version": version,
                "screen": "choose_interested_districts_three",
                "data": {
                    "selected_district_1": data_lists[0],
                    "selected_district_2": data_lists[1],
                    "selected_district_3": data_lists[2],
                    "selected_district_4": data_lists[3],
                    "selected_district_5": data_lists[4],
                    "states": selected_states,
                    "district_len": district_len,
                    "alr_selected_districts":al_selected_dists,
                    "user_existence":1,
                    "init_district": init_values
                }
            }
            logger.debug(f"district response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending district response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send district response:{e}")
        raise e




def get_area_response(version,districts,states,ph_num,telugu):
    try:
        logger.debug("sending area response")
        with get_session() as session:
            user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
            active_notifications=user_obj.active_notifications
            is_plan_active=False
            if active_notifications>0:
                is_plan_active=True
            user_selected_areas=get_selected_areas(user_obj=user_obj,telugu=telugu)       
            mandals_to_pass=get_areas_for_selected_districts(selected_districts=districts,telugu=telugu,is_plan_active=is_plan_active)
            selected_area_exmp=user_selected_areas["selected_area_exmp"]
            for dic in selected_area_exmp:
                if dic  in mandals_to_pass:
                    mandals_to_pass.remove(dic)
                mandals_to_pass.insert(0, dic)
            logger.debug(f"selected_areas_exmp:{selected_area_exmp}")
            logger.debug(f"length of the mandals to pass:{len(mandals_to_pass)}")
            if len(mandals_to_pass)>100:
                # area_len=101
                screen="choose_interested_areas_two"
                data_lists=distribute_strings(data=mandals_to_pass[:100])
            else:
                # area_len=len(mandals_to_pass)
                screen="choose_interested_areas"
                data_lists=distribute_strings(data=mandals_to_pass)
            logger.debug(f"screen:{screen}")
            init_res={
                        "select_areas_1":[],
                        "select_areas_2": [],
                        "select_areas_3": [],
                        "select_areas_4": [],
                        "select_areas_5": []
                    }
            # length_of_selected_areas=len(selected_areas)
            for dic in selected_area_exmp:
                if dic in data_lists[0]:
                    init_res["select_areas_1"].append(dic["id"])
                elif dic in data_lists[1]:
                    init_res["select_areas_2"].append(dic["id"])
                elif dic in data_lists[2]:
                    init_res["select_areas_3"].append(dic["id"])
                elif dic in data_lists[3]:
                    init_res["select_areas_4"].append(dic["id"])
                else:
                    init_res["select_areas_5"].append(dic["id"])
            response = {
                "version": version,
                "screen": screen,
                "data": {
                    "select_areas_1": data_lists[0],
                    "select_areas_2": data_lists[1],
                    "select_areas_3": data_lists[2],
                    "select_areas_4": data_lists[3],
                    "select_areas_5": data_lists[4],
                    "states": states,
                    "districts": districts,
                    "user_existence":1,
                    "alr_selected_areas":[],
                    "init_areas": init_res
                }
            }
            logger.debug(f"area response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending area response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send area response:{e}")
        raise e


def get_area_response_1(version,districts,states,ph_num,alr_selected_areas,telugu):
    try:
        logger.debug("sending area response")
        with get_session() as session:
            user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
            active_notifications=user_obj.active_notifications
            is_plan_active=False
            if active_notifications>0:
                is_plan_active=True
            user_selected_areas=get_selected_areas(user_obj=user_obj,telugu=telugu)       
            mandals_to_pass=get_areas_for_selected_districts(selected_districts=districts,telugu=telugu,is_plan_active=is_plan_active)
            selected_area_exmp=user_selected_areas["selected_area_exmp"]
            for dic in selected_area_exmp:
                if dic  in mandals_to_pass:
                    mandals_to_pass.remove(dic)
                mandals_to_pass.insert(0, dic)

            logger.debug(f"selected_areas_exmp:{selected_area_exmp}")
            if len(mandals_to_pass)>200:
                # area_len=201
                screen="choose_interested_areas_three"
                data_lists=distribute_strings(data=mandals_to_pass[100:200])
            else:
                # area_len=len(mandals_to_pass)
                screen="choose_interested_areas"
                data_lists=distribute_strings(data=mandals_to_pass[100:])
            logger.debug(f"screen:{screen}")
            init_res={
                        "select_areas_1":[],
                        "select_areas_2": [],
                        "select_areas_3": [],
                        "select_areas_4": [],
                        "select_areas_5": []
                    }
            length_of_selected_areas=len(selected_area_exmp)
            if length_of_selected_areas>100:
                for dic in selected_area_exmp:
                    if dic in data_lists[0]:
                        init_res["select_areas_1"].append(dic["id"])
                    elif dic in data_lists[1]:
                        init_res["select_areas_2"].append(dic["id"])
                    elif dic in data_lists[2]:
                        init_res["select_areas_3"].append(dic["id"])
                    elif dic in data_lists[3]:
                        init_res["select_areas_4"].append(dic["id"])
                    else:
                        init_res["select_areas_5"].append(dic["id"])
            response = {
                "version": version,
                "screen": screen,
                "data": {
                    "select_areas_1": data_lists[0],
                    "select_areas_2": data_lists[1],
                    "select_areas_3": data_lists[2],
                    "select_areas_4": data_lists[3],
                    "select_areas_5": data_lists[4],
                    "states": states,
                    "districts": districts,
                    "user_existence":1,
                    "alr_selected_areas":alr_selected_areas,
                    "init_areas": init_res
                }
            }
            logger.debug(f"area response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending area response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send area response:{e}")
        raise e

def get_area_response_2(version,districts,states,ph_num,alr_selected_areas,telugu):
    try:
        logger.debug("sending area response")
        with get_session() as session:
            user_obj=get_user_profile_for_whatsapp_users(ph_number=ph_num,session=session)
            active_notifications=user_obj.active_notifications
            is_plan_active=False
            if active_notifications>0:
                is_plan_active=True
            user_selected_areas=get_selected_areas(user_obj=user_obj,telugu=telugu)       
            mandals_to_pass=get_areas_for_selected_districts(selected_districts=districts,telugu=telugu,is_plan_active=is_plan_active)
            selected_area_exmp=user_selected_areas["selected_area_exmp"]
            for dic in selected_area_exmp:
                if dic  in mandals_to_pass:
                    mandals_to_pass.remove(dic)
                mandals_to_pass.insert(0, dic)

            logger.debug(f"selected_areas_exmp:{selected_area_exmp}")
            screen="choose_interested_areas"
            data_lists=distribute_strings(data=mandals_to_pass[200:300])
            init_res={
                        "select_areas_1":[],
                        "select_areas_2": [],
                        "select_areas_3": [],
                        "select_areas_4": [],
                        "select_areas_5": []
                    }
            length_of_selected_areas=len(selected_area_exmp)
            if length_of_selected_areas>200:
                for dic in selected_area_exmp:
                    if dic in data_lists[0]:
                        init_res["select_areas_1"].append(dic["id"])
                    elif dic in data_lists[1]:
                        init_res["select_areas_2"].append(dic["id"])
                    elif dic in data_lists[2]:
                        init_res["select_areas_3"].append(dic["id"])
                    elif dic in data_lists[3]:
                        init_res["select_areas_4"].append(dic["id"])
                    else:
                        init_res["select_areas_5"].append(dic["id"])
            response = {
                "version": version,
                "screen": screen,
                "data": {
                    "select_areas_1": data_lists[0],
                    "select_areas_2": data_lists[1],
                    "select_areas_3": data_lists[2],
                    "select_areas_4": data_lists[3],
                    "select_areas_5": data_lists[4],
                    "states": states,
                    "districts": districts,
                    "user_existence":1,
                    "alr_selected_areas":alr_selected_areas,
                    "init_areas": init_res
                }
            }
            logger.debug(f"area response:{response}")
            return response
    except SQLAlchemyError as se:
        logger.error(f"sqlachemy error while sending area response:{se}")
        raise se
    except Exception as e:
        logger.critical(f"failed to send area response:{e}")
        raise e


    
def get_area_names_in_english(area_ids):
    try:
        logger.debug("sending area names in english")
        start_time=time.time()
        supporting_areas_json=read_json_file(supporting_areas)
        area_names={}
        id_to_area = {}
        for district, areas in supporting_areas_json['areas'].items():
            for area in areas:
                id_to_area[area['id']] = area['area']+'|'+district
        for area_id in area_ids:
            area=int(area_id)
            area_str=id_to_area.get(area, "Area ID not found|District not found")
            logger.debug(f"area_name:{area_str}")
            area_name,district_name=area_str.split('|')
            if district_name not in area_names:
                if area_name=="All Areas":
                    area_names[district_name]=[f"All {district_name} Areas"]
                else:
                    area_names[district_name]=[area_name]
            else:
                if area_name=="All Areas":
                    area_names[district_name].append(f"All {district_name} Areas")
                else:
                    area_names[district_name].append(area_name)
        for district in area_names:
            area_names[district].sort()
            
        formatted_areas = "\n".join(
                [f"*{region}*:\n" + "\n".join([f"   {j + 1}. {location}" for j, location in enumerate(locations)]) for region, locations in area_names.items()]
            )
        logger.debug(f"english formated_areas;{formatted_areas}")
        endtime=time.time()
        overall=endtime-start_time
        logger.debug(f"total_time:{overall}")
        return formatted_areas
    except Exception as e:
        logger.critical(f"failed get area names in english:{e}")
        raise e


def get_area_names_in_telugu(area_ids):
    try:
        logger.debug("sending area names in telugu")
        supporting_areas_in_telugu=read_json_file(file_name=areas_in_telugu)
        area_names=""
        for i,area_id in enumerate(area_ids):
            areas_name_in_telugu=supporting_areas_in_telugu.get(area_id,"ఏ ప్రాంతం లేదు")
            if areas_name_in_telugu=="అన్ని ప్రాంతాలు":
                district_name=get_district_id(session=get_session(),area_id=int(area_id))
                district_name_in_telugu=supporting_areas_in_telugu.get(district_name,district_name)
                area_names+=f"\n{i+1}.*అన్ని {district_name_in_telugu} ప్రాంతాలు*"
            else:
                area_names+=f"\n{i+1}.*{areas_name_in_telugu}*"
        logger.debug(f"telugu area_names:{area_names}")
        return area_names
    except Exception as e:
        logger.critical(f"failed get area names in telugu:{e}")
        raise e
    
def get_message(user_name,area_names,telugu,is_areas_exceeded):
    try:
        logger.debug("sending selected areas message")
        if telugu:
            if is_areas_exceeded:
                message=(
                f"ప్రియమైన *{user_name}*,\n\n"
                "మీరు ఉచిత వినియోగదారుగా, 10 ప్రాంతాలు మాత్రమే ఎంచుకునే అవకాశం ఉంది.\n\n"
                f"మీరు ఎంచుకున్న ప్రాంతాలు:\n{area_names}\n\n"
                "మీరు మార్చాలనుకుంటే, దయచేసి */help* అని పంపండి. తర్వాత, *ప్రాంతాలను మార్చుకోండి* అనే బటన్‌పై క్లిక్ చేయండి.\n\n"
                "శుభాకాంక్షలతో,\n"
                "*Assert Experts*"
                )
            else:
                message=(
                f"ప్రియమైన *{user_name}*,\n\n"
                "మీరు దిగువ ప్రాంతాలకు విజయవంతంగా నమోదు చేసుకున్నారు..\n\n"
                f"మీరు ఎంచుకున్న ప్రాంతాలు:\n{area_names}\n\n"
                "మీరు మార్చాలనుకుంటే, దయచేసి */help* అని పంపండి. తర్వాత, *ప్రాంతాలను మార్చుకోండి* బటన్‌పై క్లిక్ చేయండి.\n\n"
                "శుభాకాంక్షలతో,\n"
                "*Assert Experts*"
                )
        else:
            if is_areas_exceeded:
                message=(
            f"Dear *{user_name}*,\n\n"
            "As a free user, you are allowed to select 10 areas only.\n\n"
            f"The areas you selected are:\n{area_names}\n\n"
            "If you want to modify, please send a message */help* . In the response, click on  *Change Intersted Areas* button.\n\n"
            "Thank you for your cooperation.\n"
            "Best regards,\n"
            "*Assert Experts*")
            else:
                message=(f"Dear *{user_name}*,\n\n"
            f"You have successfully registered for the following regions.:\n{area_names}\n\n"
            "If you want to modify, please send a message */help* . In the response, click on  *Change Intersted Areas* button.\n\n"
            "Thank you for your cooperation.\n"
            "Best regards,\n"
            "*Assert Experts*")
        logger.debug(f"whatsap message to show thier selected areas:{message}")
        return message
    except Exception as e:
        logger.critical(f"failed to send whatsap message to show thier selected areas:{e}")
        raise e
def remove_duplicates(lst):
    unique_lst = []
    for item in lst:
        if item not in unique_lst:
            unique_lst.append(item)
    return unique_lst