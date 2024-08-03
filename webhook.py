
import json
import hmac
import hashlib
import logging
from flask import Blueprint, request, Flask
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from session import get_session
from crud import add_user,get_user_profile_for_whatsapp_users,get_user_profile_for_buttons,update_user_profile_for_whatsapp_users,create_a_oreder,update_payment_status
from web_nrml_crud import get_user_selected_areas
from user_interested_areas_crud import add_selected_area,add_selected_district,add_selected_state,get_district_id,delete_user_interested_areas,delete_user_interested_districts,delete_user_interested_states,get_entire_district_id
from webhook_crud import send_flow_in_english,send_langauge_selection_template_for_update,send_message_for_order_confirmation,send_payment_flow,send_payment_template,send_langauge_selection_template,sending_help_template_in_telugu,sending_help_template_in_english,send_flow_in_english,send_flow_in_telugu,send_message_to_show_user_selected_areas,send_recent_property_flow,send_whatsapp_message,send_recent_properties_for_selected_area
from global_varibles import PLAN_FEES,VERIFY_TOKEN,APP_SECRET,NUMBER_OF_AREAS_ALLOWED_FOR_FREE_USER,whatsapp_message_to_inform_them_to_register


webhook_bp = Blueprint("whatsappbot", __name__)
supporting_areas="areas_supporting.json"
logger=logging.getLogger(__name__)

api = Api(webhook_bp)

class Whatsapp_Webhook(Resource):

    def validate_signature(self, payload, signature):
        logger.debug("validating the signature")
        try:
            expected_signature = "sha256=" + hmac.new(APP_SECRET.encode(), payload,
                                                    hashlib.sha256).hexdigest()
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.critical(f"failed to validate the signature:{e}")
            raise e

    def process_payload(self, payload):
        try:
            logger.info("Received payload: %s", payload)
            changes = payload.get('entry', [])[0].get('changes', [])[0].get('value', {})
            messages = changes.get('messages', [{}])
            profile = changes.get("contacts", [{}])[0]
            profile_name = profile.get("profile", {}).get("name", "User")
            user_phone_number = messages[0].get('from', '') 
            message_type = messages[0].get('type', '') 
            logger.debug(f"messages: {messages}")
            if messages==[{}]:
                return {"status": "fail","message":"no action taken"}
            with get_session() as session:
                user_obj = get_user_profile_for_buttons(session=session, ph_number=user_phone_number)
                prefered_langauge = user_obj.prefered_langauge if user_obj else None
                logger.debug(f"message type:{message_type}")
                if message_type == 'text':
                    message_text = messages[0]['text']['body'].lower()
                    logger.debug(f"message_text: {message_text}")
                    if message_text in ["hi", "/help", "help","start","/start"]:
                        logger.debug("sending help message")
                        return self.handle_help_message(user_phone_number=user_phone_number, user_obj=user_obj, prefered_langauge=prefered_langauge)

                    elif message_text in ["/become_a_paid_memeber", "become_a_paid_memeber"]:
                        logger.debug("sending a payment flow")
                        return send_payment_flow(recipient_id=user_phone_number)

                    elif message_text in ["/get_my_registered_areas", "get_my_registered_areas"]:
                        return self.handle_registered_areas(user_phone_number, profile_name, user_obj)
                    elif message_text in ["/recent", "recent"]:
                        return self.handle_get_recent_properties_message(recipient_id=user_phone_number,user_obj=user_obj)

                elif message_type == 'button':
                    return self.handle_button_message(messages[0], profile_name, user_phone_number, session, user_obj)

                elif message_type == 'interactive':
                    return self.handle_interactive_message(messages[0], profile_name, user_phone_number, session, user_obj)

            return {"status": "no action taken"}
        
        except IntegrityError as e:
            logger.error(f"Integrity error while handling payload: {e}")
            return {"status": "fail", "message": str(e)},400
        except SQLAlchemyError as e:
            logger.error(f"SQLAlchemy error while handling payload: {e}")
            return {"status": "fail", "message": str(e)},400
        except Exception as e:
            logger.critical(f"failed to handle payload: {e}")
            return {"status": "fail", "message": "Internal Error"},500
    def handle_help_message(self, user_phone_number, user_obj, prefered_langauge):
        try:
            logger.debug("processing for help message")
            if user_obj:
                logger.debug("user already existed")
                if prefered_langauge == "Telugu":
                    return sending_help_template_in_telugu(recipient_id=user_phone_number)
                else:
                    return sending_help_template_in_english(recipient_id=user_phone_number)
            else:
                logger.debug("new user")
                logger.debug("sending the language template")
                return send_langauge_selection_template(user_phone_number=user_phone_number)
        except Exception as e:
            logger.critical(f"failed to handle help message:{e}")
            raise e


    def handle_registered_areas(self, user_phone_number, profile_name, user_obj):
        try:
            logger.debug("sending the user's registered areas")
            telugu = user_obj.prefered_langauge == "Telugu" if user_obj else False
            if not user_obj:
                logger.debug("new user")
                logger.debug("sending the language selection template")
                return send_langauge_selection_template(user_phone_number=user_phone_number)
            else:
                # user_selected_areas = get_selected_areas(user_obj=user_obj)
                if not user_obj.is_whatsapp_user:
                    data_to_update = {"is_whatsapp_user":True}
                    update_user_profile_for_whatsapp_users(session=get_session(), user_id=user_obj.id, data_to_update=data_to_update)
                selected_areas = get_user_selected_areas(user_obj=user_obj)
                return send_message_to_show_user_selected_areas(
                    telugu=telugu, recipent_ph_num=user_phone_number, areas=selected_areas, user_name=profile_name, is_areas_exceeded=False)
        except Exception as e:
            logger.critical(f"failed to send registered areas message:{e}")
            raise e

    def handle_button_message(self, message, profile_name, user_phone_number, session, user_obj):
        try:
            logger.debug("handling _button_message")
            message_text = message['button']['text']
            payload_message = message['button']['payload']
            logger.debug(f"profile_name: {profile_name}")
            logger.debug(f"message_text: {message_text}")

            if message_text in ["Telugu", "English","తెలుగు"]:
                language = "Telugu" if message_text == "తెలుగు" or message_text=="Telugu" else "English"
                logger.debug(f"payload message: {payload_message}")
                return self.update_user_language(session, user_phone_number, profile_name, language, payload_message)

            elif message_text in ["Langauge Options", "భాషను మార్చుకోండి"]:
                logger.debug("sending template for the language change")
                return send_langauge_selection_template_for_update(user_phone_number=user_phone_number)

            elif message_text in ["Change Interested Areas", "ప్రాంతాలను మార్చుకోండి"]:
                logger.debug("sending flow for the existing user")
                if user_obj:
                    if not user_obj.is_whatsapp_user:
                        data_to_update = {"is_whatsapp_user":True}
                        update_user_profile_for_whatsapp_users(session=session, user_id=user_obj.id, data_to_update=data_to_update)
                    selected_langauge = user_obj.prefered_langauge
                    if selected_langauge == "Telugu":
                        logger.debug("sending flow in Telugu")
                        return send_flow_in_telugu(recipient_id=user_phone_number, user_existence=1)
                    else:
                        logger.debug("sending flow in English")
                        return send_flow_in_english(recipient_id=user_phone_number, user_existence=1)
                else:
                    logger.debug("new user")
                    logger.debug("sending the language template")
                    return send_langauge_selection_template(user_phone_number=user_phone_number)
            elif message_text in ["Become A Paid Member", "మెంబర్షిప్ కొరకు"]:
                logger.debug("sending payment flow")
                return send_payment_flow(recipient_id=user_phone_number)
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while handling button messages:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to handle button messages:{e}")
            raise e

    def handle_interactive_message(self, message, profile_name, user_phone_number, session, user_obj):
        try:
            logger.debug(f"profile_name: {profile_name}")
            logger.debug(f"user_number: {user_phone_number}")
            payment_obj = message.get('interactive', {}).get('payment')
            if payment_obj:
                logger.debug("Updating the payment status")
                return self.update_payment_status_of_user(payment_obj, profile_name, user_phone_number)
            data_obj = json.loads(message.get('interactive')["nfm_reply"]["response_json"])
            logger.debug(f"data_obj: {data_obj}")
            plan_type = data_obj.get("plan_type", None)
            selected_area_to_show_properties=data_obj.get("selected_area_to_show_properties",None)
            if plan_type:
                plan_value = PLAN_FEES[plan_type]["value"]
                order_id = create_a_oreder(user_id=user_phone_number, plan_type=plan_type)
                logger.debug(f"order_id: {order_id}")
                return send_payment_template(order_id=order_id, recipient_id=user_phone_number, plan_name=plan_type, fare=plan_value)
            if selected_area_to_show_properties:
                if len(selected_area_to_show_properties)==0:
                    logger.debug("no area selected to get recent properties")
                    return {"status":"success","message":"no area selected"}
                selected_area_to_show_properties=selected_area_to_show_properties[0]
                logger.debug(f"selected_area_to_show_properties:{selected_area_to_show_properties}")
                return send_recent_properties_for_selected_area(recipent_id=user_phone_number,selected_area=selected_area_to_show_properties,user_obj=user_obj)
                
            return self.update_user_interests(data_obj, profile_name, user_phone_number, session, user_obj)
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while handling interactive messages:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to handle interactive messages:{e}")
            raise e
        
    def handle_get_recent_properties_message(self,recipient_id,user_obj):
        try:
            if not user_obj:
                logger.debug("new user")
                logger.debug("sending the language template")
                return send_langauge_selection_template(user_phone_number=recipient_id)
            else:
                if not user_obj.is_whatsapp_user:
                    data_to_update = {"is_whatsapp_user":True}
                    update_user_profile_for_whatsapp_users(session=get_session(), user_id=user_obj.id, data_to_update=data_to_update)
                registered_areas=user_obj.areas
                is_telugu=user_obj.prefered_langauge=="Telugu"
                logger.debug(f"user_preferrd_langauge:{is_telugu}")
                if len(registered_areas)==0:
                    messages=whatsapp_message_to_inform_them_to_register()
                    if is_telugu:
                        message_to_send=messages.get("message_in_tel")
                    else:
                        message_to_send=messages.get("message_in_eng")
                    send_whatsapp_message(recipent_ph_num=recipient_id,message_to_send=message_to_send)
                    return send_flow_in_telugu(recipient_id=recipient_id, user_existence=1)
                else:
                    return send_recent_property_flow(recipient_id=recipient_id,is_telugu=is_telugu)
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while handling get_recent_properties messages:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to handle get_recent_properties messages:{e}")
            raise e
                
    def update_user_language(self, session, user_phone_number, profile_name, language, payload_message):
        try:
            logger.debug("updating the user selected langauge")
            with session:
                user_obj = get_user_profile_for_buttons(session=session, ph_number=user_phone_number)
                user_existence=1
                if not user_obj:
                    user_existence=0
                    logger.debug(f"adding new user with language: {language}")
                    data_to_add = {"id": user_phone_number, "name": profile_name, "ph_num_1": user_phone_number, "prefered_langauge": language,"is_whatsapp_user":True}
                    add_user(session=session, data=data_to_add)
                else:
                    user_id = user_obj.id
                    if user_obj.prefered_langauge != language:
                        data_to_update = {"prefered_langauge": language,"is_whatsapp_user":True}
                        update_user_profile_for_whatsapp_users(session=session, user_id=user_id, data_to_update=data_to_update)
                if payload_message == "flow request":
                    if language == "Telugu":
                        logger.debug("sending flow in Telugu")
                        return send_flow_in_telugu(recipient_id=user_phone_number, user_existence=user_existence)
                    else:
                        logger.debug("sending flow in English")
                        return send_flow_in_english(recipient_id=user_phone_number, user_existence=user_existence)

                return {"status": "success", "message": f"language changed successfully to {language}"}
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while updating prefered langauge:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to updating prefered langauge:{e}")
            raise e

    def update_payment_status_of_user(self, payment_obj, profile_name, ph_num):
        try:
            logger.debug("updating the payment status")
            transaction_id = payment_obj.get("transaction_id")
            transaction_type = payment_obj.get("transaction_type")
            reference_id = payment_obj.get("reference_id")
            total_amount = payment_obj.get("total_amount")
            fare = total_amount["value"] / total_amount["offset"]
            status = payment_obj.get("status")
            
            if status == "success":
                plan_details = update_payment_status(order_id=reference_id, transaction_id=transaction_id,
                                                    transaction_type=transaction_type, price=fare)
                logger.debug(f"fare: {fare}")
                subscription_plan_type = plan_details["subscription_plan_type"]
                plan_starts_at = plan_details["plan_starts_at"]
                plan_ends_at = plan_details["plan_ends_at"]
                send_message_for_order_confirmation(
                    recipent_ph_num=ph_num, plan=subscription_plan_type, fare=fare, user_name=profile_name,
                    from_date=plan_starts_at, to_date=plan_ends_at)
                return {"status": "success", "message": "updated successfully"}
            else:
                return {"status": "success"}
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while updating payment status:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to updating payment status:{e}")
            raise e

    def update_user_interests(self, data_obj, profile_name, user_phone_number, session, user_obj):
        try:
            logger.debug("updating user intersted areas")
            states = data_obj.get("states")
            districts = data_obj.get("districts")
            mandals = data_obj.get("areas")
            user_existence = int(data_obj.get("user_existence"))
            selected_langauge = data_obj.get("Telugu", None)
            logger.debug(f"districts: {districts}")
            logger.debug(f"mandals: {mandals}")
            logger.debug(f"states: {states}")
            logger.debug(f"user_existence: {user_existence}")
            logger.debug(f"selected_langauge: {selected_langauge}")
            with session:
                if user_existence == 1:
                    return self.update_existing_user_interests(session, user_phone_number, profile_name, states, districts, mandals, user_obj)
                else:
                    return self.add_new_user_interests(session, user_phone_number, profile_name, states, districts, mandals)
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while updating intersted areas:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to updating intersted areas:{e}")
            raise e
    def update_existing_user_interests(self, session, user_phone_number, profile_name, states, districts, mandals, user_obj):
        try:
            logger.debug("adding areas to the existing user")
            user_id = user_obj.id
            # selected_states = get_selected_states(user_obj=user_obj)
            selected_states=[s.id for s in user_obj.states]
            # user_selected_districts = get_selected_districts(user_obj=user_obj)
            # selected_districts = user_selected_districts["selected_districts"]
            selected_districts=[d.id for d in user_obj.districts]
            # user_selected_areas = get_selected_areas(user_obj=user_obj)
            # selected_areas = user_selected_areas["selected_areas"]
            selected_areas=[a.id for a in user_obj.areas]
            is_areas_exceeded = False
            #deleting the existing areas
            for state in selected_states:
                if state not in states:
                    delete_user_interested_states(session=session, state_id=state, user_id=user_id)

            for area_id in selected_areas:
                if str(area_id) not in mandals:
                    delete_user_interested_areas(session=session, user_id=user_id, area_id=area_id)

            for district in selected_districts:
                if district not in districts:
                    delete_user_interested_districts(session=session, user_id=user_id, district_id=district)
            #adding new areas
            for district in districts:
                if district not in selected_districts:
                    add_selected_district(session=session, user_id=user_id, district=district)
            is_free_user = user_obj.active_notifications <= 0
            logger.debug(f"if free user:{is_free_user}") 
            if is_free_user and len(mandals) > NUMBER_OF_AREAS_ALLOWED_FOR_FREE_USER:
                mandals = mandals[:NUMBER_OF_AREAS_ALLOWED_FOR_FREE_USER]
                is_areas_exceeded = True
            selected_areas=[a.id for a in user_obj.areas]
            logger.debug(f"selected areas:{selected_areas}")
            district_id_mapping={}
            for mandal in mandals:
                area_id = int(mandal)
                district_name = get_district_id(session=session, area_id=area_id)
                if district_name in district_id_mapping:
                    entire_district_id=district_id_mapping[district_name]
                else:
                    entire_district_id = get_entire_district_id(session=session, district_id=district_name)
                    district_id_mapping[district_name]=entire_district_id 
                logger.debug(f"entire district id:{entire_district_id}")
                if (entire_district_id in selected_areas) or (area_id in selected_areas):
                    continue
                elif entire_district_id == area_id:
                    add_selected_area(session=session, area_id=entire_district_id, user_id=user_id, district_id=district_name, action=True)
                    selected_areas.append(entire_district_id)
                else:
                    add_selected_area(session=session, area_id=area_id, user_id=user_id, district_id=district_name, action=False)

            for state in states:
                if state not in selected_states:
                    add_selected_state(session=session, user_id=user_id, state=state)

            logger.debug("Data updated successfully")
            telugu = user_obj.prefered_langauge == 'Telugu'
            # user_selected_areas = get_selected_areas(user_obj=user_obj)
            selected_areas = get_user_selected_areas(user_obj=user_obj)
            return send_message_to_show_user_selected_areas(
                telugu=telugu, recipent_ph_num=user_phone_number, areas=selected_areas, user_name=profile_name, is_areas_exceeded=is_areas_exceeded)
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while updating existing intersted areas:{se}")
            raise se
        except Exception as e:
            logger.critical(f"failed to updating existing intersted areas:{e}")
            raise e

    def add_new_user_interests(self, session, user_phone_number, profile_name, states, districts, mandals):
        try:
            logger.debug("adding intrested areas")
            for district in districts:
                add_selected_district(session=session, user_id=user_phone_number, district=district)
            is_areas_exceeded = False
            if len(mandals) > NUMBER_OF_AREAS_ALLOWED_FOR_FREE_USER:
                mandals = mandals[:NUMBER_OF_AREAS_ALLOWED_FOR_FREE_USER]
                is_areas_exceeded = True
            for mandal in mandals:
                area_id = int(mandal)
                add_selected_area(session=session, area_id=area_id, user_id=user_phone_number, district_id="visakhapatnam", action=False)
            for state in states:
                add_selected_state(session=session, user_id=user_phone_number, state=state)
            user_obj = get_user_profile_for_whatsapp_users(session=session, ph_number=user_phone_number)
            telugu = user_obj.prefered_langauge == 'Telugu'
            send_message_to_show_user_selected_areas(
                telugu=telugu, recipent_ph_num=user_phone_number, areas=mandals, user_name=profile_name, is_areas_exceeded=is_areas_exceeded)
            return send_recent_property_flow(recipient_id=user_phone_number,is_telugu=telugu)
        except SQLAlchemyError as se:
            logger.error(f"sqlachemy error while adding intersted areas:{se}")
            raise se
        except Exception as e:
            logger.critical(f"faile to add intersted areas:{e}")
            raise e

    def get(self):
        try:
            logger.info("verifying the webhook")
            hub_mode = request.args.get('hub.mode')
            hub_challenge = request.args.get('hub.challenge')
            hub_verify_token = request.args.get('hub.verify_token')
            if hub_mode == 'subscribe' and hub_verify_token == VERIFY_TOKEN:
                return Flask.response_class(hub_challenge, mimetype='text/plain')
            else:
                return "Verification failed", 403
        except Exception as e:
            logger.critical(f"failed to verify during whatsaap req:{e}")
            return {"status":"fail","message":"Internall Error"},500

    def post(self):
        try:
            body = json.loads(request.data)
            logging.info("Payload: %s", body)
            if body:
                signature = request.headers.get('X-Hub-Signature-256')
                if not signature or not self.validate_signature(
                        request.data, signature):
                    return {"status":"fail","message":"Signature validation failed"}, 403
                return self.process_payload(body)
        except Exception as e:
            logger.critical(f"Exception in webhook:{e}")
            return {"status":"fail","message":"Internall Error"},500

api.add_resource(Whatsapp_Webhook, '/webhooks')






