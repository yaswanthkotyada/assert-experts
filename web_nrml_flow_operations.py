import logging
import random
from sqlalchemy.exc import SQLAlchemyError
from crud import read_file, get_user_profile_for_whatsapp_users, get_district_object, read_json_file
from session import get_session
from web_nrml_crud import (distribute_strings, get_init_res, get_init_res_1,
                           sending_districts_first_screen, get_area_response,
                           get_district_response_1, get_district_response_2,
                           get_area_response_1, get_area_response_2,
                           get_areas_for_selected_districts,
                           get_districts_from_file,remove_duplicates)
from global_varibles import PLAN_FEES, NUMBER_OF_ALL_AREAS, NUMBER_OF_AREAS_IN_A_DISTRICT, DEFAULT_PROPERTY_AREAS

areas_in_telugu = "areas_in_Telugu.json"
supporting_areas = "areas_supporting.json"
asserts_experts_logo_uft8 = "asserts_experts_logo_uft8.txt"

logger = logging.getLogger(__name__)


class PayloadProcessor:

    def __init__(self):
        self.telugu = False

    def process_payload(self, payload):
        try:
            logger.info(f"payload:{payload}")
            version = payload.get("version")
            action = payload.get("action")
            screen = payload.get("screen")
            data = payload.get("data", {})
            flow_token = payload.get("flow_token", None)
            if flow_token:
                self._parse_flow_token(flow_token)
            logger.debug(
                f"Processing version: {version}, action: {action}, screen: {screen}"
            )
            if action == "ping":
                return self._handle_ping(version)
            elif action == "INIT":
                return self._handle_init(version)
            elif action == "BACK":
                return self._handle_back(version)
            elif action == "data_exchange":
                return self._handle_data_exchange(version, screen, data)
            else:
                return self._handle_invalid_action(version, screen)

        except SQLAlchemyError as se:
            raise se
        except Exception as e:
            raise e

    def _parse_flow_token(self, flow_token):
        try:
            data_from_webhook = flow_token.split("|")
            self.ph_num = data_from_webhook[1]
            langauge = int(data_from_webhook[2])
            self.user_obj_from_webhook = int(data_from_webhook[3])
            self.telugu = langauge == 1
            logger.debug(
                f"Parsed flow token - ph_num: {self.ph_num}, langauge: {langauge}, user_obj: {self.user_obj_from_webhook}, telugu: {self.telugu}"
            )
        except Exception as e:
            raise e

    def _handle_ping(self, version):
        return {"version": version, "data": {"status": "active"}}

    def _handle_init(self, version):
        try:
            logger.debug("Processing INIT action for first screen")
            return get_init_res(ph_num=self.ph_num,
                                version=version,
                                telugu=self.telugu,
                                user_existence=self.user_obj_from_webhook)
        except Exception as e:
            raise e

    def _handle_back(self, version):
        return {"version": version, "screen": "property_selection", "data": {}}

    def _handle_data_exchange(self, version, screen, data):
        try:
            if screen == "choose_interested_states" or screen == "choose_interested_states_rentry":
                return self._handle_choose_interested_states(
                    version, screen, data)
            elif screen == "choose_interested_districts":
                return self._handle_choose_interested_districts(version, data)
            elif screen == "choose_interested_districts_two":
                return self._handle_choose_interested_districts_two(
                    version, data)
            elif screen == "choose_interested_districts_three":
                return self._handle_choose_interested_districts_three(
                    version, data)
            elif screen == "choose_interested_areas_two":
                return self._handle_choose_interested_areas_two(version, data)
            elif screen == "choose_interested_areas_three":
                return self._handle_choose_interested_areas_three(
                    version, data)
            elif screen == "choose_interested_areas":
                return self._handle_choose_interested_areas(version, data)
            else:
                return self._handle_invalid_screen(version, screen)
        except SQLAlchemyError as se:
            raise se
        except Exception as e:
            raise e

    def _handle_invalid_action(self, version, screen):
        return {
            "version": version,
            "screen": screen,
            "data": {
                "error_message": "Invalid action"
            }
        }

    def _handle_invalid_screen(self, version, screen):
        return {
            "version": version,
            "screen": screen,
            "data": {
                "error_message": "Invalid screen"
            }
        }

    def _handle_choose_interested_states(self, version, screen, data):
        try:
            logger.debug("_handling_choose_interested_states")
            # selected_states = list(set(data.get("state_1", [])))
            selected_states = data.get("state_1", [])
            user_existence = int(data["user_existence"])
            logger.debug(
                f"Selected states: {selected_states}, user existence: {user_existence}"
            )
            return sending_districts_first_screen(
                selected_states=selected_states,
                version=version,
                screen=screen,
                user_existence=user_existence,
                ph_num=self.ph_num,
                telugu=self.telugu)
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while _handle_choose_interested_states:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_states:{e}")
            raise e

    def _handle_choose_interested_districts(self, version, data):
        try:
            logger.debug("_handling_choose_interested_districts")
            selected_states = data["states"]
            districts = data.get("districts_1", []) + data.get("districts_2", [])
            districts=remove_duplicates(lst=districts)
            district_len = int(data["district_len"])
            user_existence = int(data["user_existence"])
            logger.debug(
                f"Selected districts: {districts}, district length: {district_len}, user existence: {user_existence}"
            )
            if district_len > 40:
                if user_existence == 1:
                    return get_district_response_1(
                        selected_states=selected_states,
                        version=version,
                        ph_num=self.ph_num,
                        al_selected_dists=districts,
                        telugu=self.telugu)
                else:
                    return self._handle_large_district_selection(
                        version, selected_states, districts)
            else:
                return self._handle_mandals_selection(version, selected_states,
                                                      districts,
                                                      user_existence)
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while _handle_choose_interested_districts:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_districts:{e}")
            raise e

    def _handle_large_district_selection(self, version, selected_states,
                                         districts):
        try:
            logger.debug("_handling_large_district_selection")

            districs_to_send = get_districts_from_file(
                selected_states=selected_states, telugu=self.telugu)

            if len(districs_to_send) > 140:
                district_len = 141
                data_lists = distribute_strings(data=districs_to_send[40:140])
            else:
                district_len = len(districs_to_send)
                data_lists = distribute_strings(data=districs_to_send[40:])

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
                    "alr_selected_districts": districts,
                    "user_existence": 0,
                    "init_district": {
                        "selected_district_1": []
                    }
                }
            }
            logger.debug(f"district response:{response}")
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while _handle_large_district_selection:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_large_district_selection:{e}")
            raise e

    def _handle_mandals_selection(self, version, selected_states, districts,
                                  user_existence):
        try:
            logger.debug("_handling__mandals_selection")
            if districts:
                if user_existence == 1:
                    return get_area_response(version=version,
                                             districts=districts,
                                             states=selected_states,
                                             ph_num=self.ph_num,
                                             telugu=self.telugu)
                else:
                    mandals_to_pass = get_areas_for_selected_districts(
                        selected_districts=districts, telugu=self.telugu)
                    # logger.debug(f"mandal to pass:{mandals_to_pass}")
                    return self._prepare_mandals_response(
                        version, selected_states, districts, mandals_to_pass)
            else:
                return get_init_res_1(ph_num=self.ph_num,
                                      version=version,
                                      telugu=self.telugu,
                                      user_existence=user_existence)
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while _handle_mandals_selection:{se}")
            raise se
        except Exception as e:
            logger.critical(f"while handling _handle_mandals_selection:{e}")
            raise e

    def _prepare_mandals_response(self, version, selected_states, districts,
                                  mandals_to_pass):
        try:
            if len(mandals_to_pass) > 100:
                screen = "choose_interested_areas_two"
                data_lists = distribute_strings(data=mandals_to_pass[:100])
            else:
                screen = "choose_interested_areas"
                data_lists = distribute_strings(data=mandals_to_pass)

            response = {
                "version": version,
                "screen": screen,
                "data": {
                    "select_areas_1": data_lists[0],
                    "select_areas_2": data_lists[1],
                    "select_areas_3": data_lists[2],
                    "select_areas_4": data_lists[3],
                    "select_areas_5": data_lists[4],
                    "states": selected_states,
                    "districts": districts,
                    "user_existence": 0,
                    "alr_selected_areas": [],
                    "init_areas": {}
                }
            }

            logger.debug(f"areas response:{response}")
            return response
        except Exception as e:
            logger.critical(
                f"exception while handling _prepare_mandals_response:{e}")
            raise e

    def _handle_choose_interested_districts_two(self, version, data):
        try:
            selected_states = data["states"]
            districts = data.get("alr_selected_districts", []) + data.get(
                "districts_1", []) + data.get("districts_2", []) + data.get(
                    "districts_3", []) + data.get(
                        "districts_4", []) + data.get("districts_5", [])
            districts=remove_duplicates(lst=districts)
            district_len = int(data["district_len"])
            user_existence = int(data["user_existence"])
            logger.debug(f"Handling choose_interested_districts_two - selected states: {selected_states}, districts: {districts}, district length: {district_len}"
            )
            if district_len > 140:
                if user_existence == 1:
                    response = get_district_response_2(
                        selected_states=selected_states,
                        version=version,
                        ph_num=self.ph_num,
                        al_selected_dists=districts,
                        telugu=self.telugu)
                else:
                    # district_data = json.loads(read_file(districts_file))
                    districs_to_send = get_districts_from_file(
                        selected_states=selected_states, telugu=self.telugu)
                    logger.debug(f"districts:{districs_to_send[0]}")
                    district_len = len(districs_to_send)
                    data_lists = distribute_strings(
                        data=districs_to_send[140:240])
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
                            "alr_selected_districts": districts,
                            "user_existence": 0,
                            "init_district": {
                                "selected_district_1": []
                            }
                        }
                    }
                logger.debug(f"district response:{response}")
                return response
            else:
                return self._handle_mandals_selection(version, selected_states,
                                                      districts,
                                                      user_existence)
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while handling _handle_choose_interested_districts_two:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_districts_two:{e}")
            raise e

    def _handle_choose_interested_districts_three(self, version, data):
        try:
            selected_states = data["states"]
            districts = data.get("alr_selected_districts", []) + data.get(
                "districts_1", []) + data.get("districts_2", []) + data.get(
                    "districts_3", []) + data.get(
                        "districts_4", []) + data.get("districts_5", [])
            districts=remove_duplicates(districts)
            # district_len=int(data["district_len"])
            user_existence = int(data["user_existence"])
            logger.debug(
                f"Handling choose_interested_districts_three - selected states: {selected_states}, districts: {districts}"
            )

            return self._handle_mandals_selection(version, selected_states,
                                                  districts, user_existence)
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while handling _handle_choose_interested_districts_three:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_districts_three:{e}"
            )
            raise e

    def _handle_choose_interested_areas_two(self, version, data):
        try:
            selected_states = data["states"]
            selected_districts = data["districts"]
            areas = data.get("areas_1", []) + data.get(
                "areas_2", []) + data.get("areas_3", []) + data.get(
                    "areas_4", []) + data.get("areas_5", [])
            areas=remove_duplicates(lst=areas)
            user_existence = int(data["user_existence"])
            if user_existence == 1:
                return get_area_response_1(version=version,
                                           districts=selected_districts,
                                           states=selected_states,
                                           ph_num=self.ph_num,
                                           alr_selected_areas=areas,
                                           telugu=self.telugu)
            else:
                mandals_to_pass = get_areas_for_selected_districts(
                    selected_districts=selected_districts, telugu=self.telugu)
                if len(mandals_to_pass) > 200:
                    # area_len=201
                    screen = "choose_interested_areas_three"
                    data_lists = distribute_strings(
                        data=mandals_to_pass[100:200])
                else:
                    # area_len=len(mandals_to_pass)
                    screen = "choose_interested_areas"
                    data_lists = distribute_strings(data=mandals_to_pass[100:])
                logger.debug(f"screen:{screen}")
                response = {
                    "version": version,
                    "screen": screen,
                    "data": {
                        "select_areas_1": data_lists[0],
                        "select_areas_2": data_lists[1],
                        "select_areas_3": data_lists[2],
                        "select_areas_4": data_lists[3],
                        "select_areas_5": data_lists[4],
                        "states": selected_states,
                        "districts": selected_districts,
                        "user_existence": 0,
                        "alr_selected_areas": areas,
                        "init_areas": {
                            "select_areas": []
                        }
                    }
                }
                logger.debug(f"areas response:{response}")
                return response
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while handling _handle_choose_interested_areas_two:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_areas_two:{e}")
            raise e

    def _handle_choose_interested_areas_three(self, version, data):
        try:
            selected_states = data["states"]
            selected_districts = data["districts"]
            areas = data.get("alr_selected_areas", []) + data.get(
                "areas_1", []) + data.get("areas_2", []) + data.get(
                    "areas_3", []) + data.get("areas_4", []) + data.get(
                        "areas_5", [])
            areas=remove_duplicates(lst=areas)
            user_existence = int(data["user_existence"])
            logger.debug(
                f"Handling choose_interested_areas_three - selected states: {selected_states}, selected districts: {selected_districts}, areas: {areas} ,user_existence :{user_existence}"
            )
            if user_existence == 1:
                return get_area_response_2(version=version,
                                           districts=selected_districts,
                                           states=selected_states,
                                           ph_num=self.ph_num,
                                           alr_selected_areas=areas,
                                           telugu=self.telugu)
            else:
                mandals_to_pass = get_areas_for_selected_districts(
                    selected_districts=selected_districts, telugu=self.telugu)
                screen = "choose_interested_areas"
                data_lists = distribute_strings(data=mandals_to_pass[200:300])
                logger.debug(f"screen:{screen}")
                response = {
                    "version": version,
                    "screen": screen,
                    "data": {
                        "select_areas_1": data_lists[0],
                        "select_areas_2": data_lists[1],
                        "select_areas_3": data_lists[2],
                        "select_areas_4": data_lists[3],
                        "select_areas_5": data_lists[4],
                        "alr_selected_areas": areas,
                        "user_existence": 0,
                        "states": selected_states,
                        "districts": selected_districts,
                        "init_areas": {}
                    }
                }
                logger.debug(f"areas response:{response}")
                return response
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while handling _handle_choose_interested_areas_three:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_areas_three:{e}")
            raise e

    def _handle_choose_interested_areas(self, version, data):
        try:
            selected_states = data["states"]
            selected_districts = data["districts"]
            areas = data.get("alr_selected_areas", []) + data.get(
                "areas_1", []) + data.get("areas_2", []) + data.get(
                    "areas_3", []) + data.get("areas_4", []) + data.get(
                        "areas_5", [])
            areas=remove_duplicates(lst=areas)
            user_existence = int(data["user_existence"])
            logger.debug(
                f"Handling choose_interested_areas - selected states: {selected_states}, selected districts: {selected_districts}, areas: {areas}"
            )
            if areas:
                response = {
                    "version": version,
                    "screen": "SUCCESS",
                    "data": {
                        "extension_message_response": {
                            "params": {
                                "states": data.get("states"),
                                "districts": data.get("districts"),
                                "areas": areas,
                                "user_existence": user_existence,
                                'Telugu': self.telugu
                            }
                        }
                    }
                }
                logger.debug(f"areas response:{response}")
                return response
            else:
                logger.debug("sending back to first screen")
                return get_init_res_1(version=version,
                                      ph_num=self.ph_num,
                                      telugu=self.telugu,
                                      user_existence=user_existence)
        except SQLAlchemyError as se:
            logger.error(
                f"sqlalchemy error while handling _handle_choose_interested_areas:{se}"
            )
            raise se
        except Exception as e:
            logger.critical(
                f"while handling _handle_choose_interested_areas:{e}")
            raise e

    def process_payload_for_payment(self, payload):
        try:
            logger.debug(f"recived payload for payment:{payload}")
            version = payload.get("version")
            action = payload.get("action")
            screen = payload.get("screen")
            data = payload.get("data", {})
            flow_token = payload.get("flow_token", None)
            if action == "ping":
                response = {"version": version, "data": {"status": "active"}}
            elif action == "INIT":
                logger.debug("processing for first screen of subscription")
                plans_to_send = [{
                    "id": plan_name,
                    "title": plan_name.capitalize()
                } for plan_name in PLAN_FEES]
                asserts_experts_logo_uft8_url = read_file(
                    asserts_experts_logo_uft8)
                response = {
                    "version": version,
                    "screen": "subscription",
                    "data": {
                        "select_plan": plans_to_send,
                        "img_url": asserts_experts_logo_uft8_url,
                        "total": PLAN_FEES["classic"]["text_for_flow"],
                        "plan_init_values": {
                            "select_plan": "classic"
                        }
                    }
                }
            elif action == "data_exchange":
                selected_plan = data.get("plan_type", "classic")
                fare_text = PLAN_FEES[selected_plan]["text_for_flow"]
                response = {
                    "version": version,
                    "screen": "subscription",
                    "data": {
                        # "select_plan":plan_type,
                        # "img_url":asserts_experts_logo_uft8,
                        "total": fare_text,
                        "plan_init_values": {
                            "select_plan": selected_plan
                        }
                    }
                }
            logger.debug(f"payment flow response:{response}")
            return response
        except Exception as e:
            logger.error(f"Exception during flow for payment:{e}")
            raise e

    def process_payload_for_recent_properties(self, payload):
        try:
            logger.debug(f"recived payload for recent properties:{payload}")
            version = payload.get("version")
            action = payload.get("action")
            screen = payload.get("screen")
            data = payload.get("data", {})
            flow_token = payload.get("flow_token", None)
            if flow_token:
                data_from_webhook = flow_token.split("|")
                self.ph_num = data_from_webhook[1]
                # self.ph_num ="919542926041"
            if action == "ping":
                response = {"version": version, "data": {"status": "active"}}
            elif action == "INIT":
                with get_session() as session:
                    user_obj = get_user_profile_for_whatsapp_users(
                        session=session, ph_number=self.ph_num)
                    if not user_obj:
                        areas_to_send = DEFAULT_PROPERTY_AREAS
                        sorted_areas_to_send = sorted(
                            areas_to_send, key=lambda area: area["id"])
                        response = {
                            "version": version,
                            "screen": "select_area",
                            "data": {
                                "select_area": sorted_areas_to_send,
                                "is_telugu": False,
                                # "img_url":asserts_experts_logo_uft8_url,
                                "init_areas": {
                                    "select_area": []
                                }
                            }
                        }
                        logger.debug(f"flow response:{response}")
                        return response
                    prefered_langauge = user_obj.prefered_langauge
                    self.telugu = prefered_langauge == "Telugu"
                    if self.telugu:
                        return self.handle_init_for_telugu_user(
                            version, user_obj=user_obj, session=session)
                    else:
                        return self.handle_init_for_english_user(
                            version, user_obj=user_obj, session=session)

        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            logger.critical(
                f"Exception during selecting of area to get recent properties:{e}"
            )
            raise e

    def handle_init_for_english_user(self, version, user_obj, session):
        try:
            logger.debug("processing for sending user registered areas")
            area_names_to_send = []
            all_area_districts = []
            area_names = []
            for area_obj in user_obj.areas:
                area_name = area_obj.name
                if area_name == "All Areas":
                    all_area_districts.append(area_obj.district_id)
                else:
                    area_names.append({"id": area_name, "title": area_name})
            n = min(NUMBER_OF_ALL_AREAS, len(all_area_districts))
            all_area_districts = random.sample(all_area_districts, n)
            max_count_areas = NUMBER_OF_AREAS_IN_A_DISTRICT
            total_areas_names_to_sent=n*max_count_areas+len(area_names)
            if total_areas_names_to_sent<20:
                count=20-total_areas_names_to_sent
                max_count_areas+=count
            logger.debug(f"max_count_areas:{max_count_areas}")
            for district_id in all_area_districts:
                district_object = get_district_object(session=session,
                                                      district_id=district_id)
                if district_object:
                    area_objs = district_object.areas
                    totall_number_of_areas = len(area_objs)
                    if totall_number_of_areas < max_count_areas:
                        max_count_areas = totall_number_of_areas
                    area_objs = random.sample(area_objs, max_count_areas)
                    for area_obj in area_objs:
                        area_name = area_obj.name
                        if area_name == "All Areas":
                            continue
                        area_names_to_send.append({
                            "id": area_name,
                            "title": area_name
                        })

            logger.debug(f"area_names_to_send:{area_names_to_send}")
            logger.debug(f"area_names:{area_names}")
            len_of_area_names_to_send = len(area_names_to_send)
            if len_of_area_names_to_send < 20:  #there 20 is the page size in the flow as it is constant i didn't put in global varibles
                num_ares_to_add_in_res = 20 - len_of_area_names_to_send
                area_names_to_send.extend(area_names[:num_ares_to_add_in_res])
            logger.debug(f'registered area names:{area_names_to_send}')
            if len(area_names_to_send) == 0:
                area_names_to_send = DEFAULT_PROPERTY_AREAS
            sorted_areas_to_send = sorted(area_names_to_send,
                                          key=lambda area: area["id"])
            # asserts_experts_logo_uft8_url=read_file(asserts_experts_logo_uft8)
            response = {
                "version": version,
                "screen": "select_area",
                "data": {
                    "select_area": sorted_areas_to_send,
                    "is_telugu": False,
                    # "img_url":asserts_experts_logo_uft8_url,
                    "init_areas": {
                        "select_area": []
                    }
                }
            }
            logger.debug(f"flow response:{response}")
            return response
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e

    def handle_init_for_telugu_user(self, version, user_obj, session):
        try:
            logger.debug("processing for sending user registered areas")
            area_names_in_tel_json = read_json_file(file_name=areas_in_telugu)
            area_names_to_send = []
            all_area_districts = []
            area_names = []
            for area_obj in user_obj.areas:
                area_name = area_obj.name
                if area_name == "All Areas":
                    all_area_districts.append(area_obj.district_id)
                else:
                    area_name_in_tel = area_names_in_tel_json.get(
                        str(area_obj.id), area_name)
                    area_names.append({
                        "id": area_name,
                        "title": area_name_in_tel
                    })
            n = min(NUMBER_OF_ALL_AREAS, len(all_area_districts))
            all_area_districts = random.sample(all_area_districts, n)
            max_count_areas = NUMBER_OF_AREAS_IN_A_DISTRICT
            for district_id in all_area_districts:
                district_object = get_district_object(session=session,
                                                      district_id=district_id)
                if district_object:
                    area_objs = district_object.areas
                    totall_number_of_areas = len(area_objs)
                    if totall_number_of_areas < max_count_areas:
                        max_count_areas = totall_number_of_areas
                    area_objs = random.sample(area_objs, max_count_areas)
                    for area_obj in area_objs:
                        area_name = area_obj.name
                        if area_name == "All Areas":
                            continue
                        area_name_in_tel = area_names_in_tel_json.get(
                            str(area_obj.id), area_name)
                        area_names_to_send.append({
                            "id": area_name,
                            "title": area_name_in_tel
                        })
            len_of_area_names_to_send = len(area_names_to_send)
            if len_of_area_names_to_send < 20:  #here 20 is the page size in the flow as it is constant i didn't put in global varibles
                num_ares_to_add_in_res = 20 - len_of_area_names_to_send
                area_names_to_send.extend(area_names[:num_ares_to_add_in_res])
            logger.debug(f'registered area names:{area_names_to_send}')
            if len(area_names_to_send) == 0:
                area_names_to_send = DEFAULT_PROPERTY_AREAS
            sorted_areas_to_send = sorted(area_names_to_send,
                                          key=lambda area: area["id"])

            # asserts_experts_logo_uft8_url=read_file(asserts_experts_logo_uft8)
            response = {
                "version": version,
                "screen": "select_area",
                "data": {
                    "select_area": sorted_areas_to_send,
                    "is_telugu": True,
                    # "img_url":asserts_experts_logo_uft8_url,
                    "init_areas": {
                        "select_area": []
                    }
                }
            }
            logger.debug(f"flow response:{response}")
            return response
        except SQLAlchemyError as e:
            raise e
        except Exception as e:
            raise e
