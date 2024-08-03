import logging
import requests
from models import Property,Area
from sqlalchemy.exc import SQLAlchemyError
from session import get_session
from sqlmodel import select,and_
from global_varibles import PLAN_FEES,ACCESS_TOKEN,ASSERT_EXPERTS_LOGO_URL,PHONE_NUMBER_ID_FOR_WHATSAPP,NUMBER_OF_PROPERTIES_TO_SEND_FOR_RECENT_PROPERTIES_REQUEST,whatsapp_template_names,whatsapp_message_to_inform_them_to_register
from crud import get_start_end_dates,send_whatsapp_notifications_to_single_user
from web_nrml_crud import get_area_names_in_english,get_area_names_in_telugu,get_message

logger=logging.getLogger(__name__)

def send_langauge_selection_template(user_phone_number):
    try:
        logger.debug("sending langauge selection template")
        template_names=whatsapp_template_names()
        lang_selection_temp_name=template_names.get("langauge_selection_temp_name",None)
        payload = {
        "messaging_product": "whatsapp",
            "to": user_phone_number,
            "type": "template",
            "template": {
                "name": lang_selection_temp_name,
                "language": {
                    "code": "en"
                },
                "components": [{
                    "type": "header",
                    "parameters": []
                }, {
                    "type": "body",
                    "parameters": []
                }, {
                    "type":"button",
                    "sub_type":"quick_reply",
                    "index":0,
                    "parameters": [{
                        "type": "payload",
                        "payload": "flow request"
                    }]
                }, {
                    "type":"button",
                    "sub_type":"quick_reply",
                    "index":1,
                    "parameters": [{
                        "type": "payload",
                        "payload": "flow request"
                    }]
                }]
            }
        }
        response = requests.post(
            f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"},200
    except Exception as e:
        logger.critical(f"failed to send langeuge selection temp:{e}")
        raise e

def send_langauge_selection_template_for_update(user_phone_number):
    try:
        logger.debug("sending langauge selection template for update")
        template_names=whatsapp_template_names()
        lang_selection_temp_name=template_names.get("langauge_selection_temp_name",None)
        payload = {
        "messaging_product": "whatsapp",
            "to": user_phone_number,
            "type": "template",
            "template": {
                "name": lang_selection_temp_name,
                "language": {
                    "code": "en"
                },
                "components": [{
                    "type": "header",
                    "parameters": []
                }, {
                    "type": "body",
                    "parameters": []
                }, {
                    "type":"button",
                    "sub_type":"quick_reply",
                    "index":0,
                    "parameters": [{
                        "type": "payload",
                        "payload": "change"
                    }]
                }, {
                    "type":"button",
                    "sub_type":"quick_reply",
                    "index":1,
                    "parameters": [{
                        "type": "payload",
                        "payload": "change"
                    }]
                }]
            }
        }
        response = requests.post(
            f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"},200
    except Exception as e:
        logger.critical(f"failed to send languge selection template:{e}")
        raise e

def send_payment_template(plan_name,fare,order_id,recipient_id):
    try:    
        logger.debug("sending payment template")
        logger.debug(f"fare:{fare}")            
        plan_duration=PLAN_FEES[plan_name]["period_in_months"]
        plan_starts_from,plan_ends_at=get_start_end_dates(months=plan_duration)
        plan_name=plan_name.capitalize()
        logger.debug(f"plan_name:{plan_name}")
        # Retrieve recipient's phone number and message content from the request body
        recipient = recipient_id
        message=f"Plan Name:*{plan_name}*\nPlan Validity:*{plan_starts_from} to {plan_ends_at}*\nFee:*{fare} RS*\nPurpose:To Get Property Notifications"
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload ={
    "messaging_product": "whatsapp",
    "recipient_type": "individual",
    "to": recipient,
    "type": "interactive",        
    "interactive": {
        "type": "order_details",
        "body": {            
        "text":message
        },
        "action": {
        "name": "review_and_pay",
        "parameters": {
            "reference_id": order_id,
            "type": "digital-goods",
            "payment_type": "upi",
            "payment_configuration": "AssertExperts",
            "currency": "INR",
            "total_amount": {
            "value": fare*100,
            "offset": 100
            },
            "order": {
            "status": "pending",
            "items": [
                {
                "name": "Assert Experts",
                "amount": {
                    "value": fare*100,
                    "offset": 100
                },
                "quantity": 1
            }
        ],
        "subtotal": {
            "value": fare*100,
            "offset": 100
        }
                }
            }
            }
        }
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        
        return {"status":"success"},200
    except Exception as e:
        logger.critical(f"Failed to send payment template:{e}")
        return {"status":"success","message":"Internal error"}, 500

def sending_help_template_in_english( recipient_id):
    logger.debug("sending help template in english")
    
    try:
        template_names=whatsapp_template_names()
        help_temp_name=template_names.get("help_template_in_english")
        payload={
            "messaging_product":"whatsapp",
            "to":recipient_id,
            "type":"template",
            "template":{
                "name":help_temp_name,
                "language":{
                    "code":"en"
                },
                "components":[
                    {
                        "type":"header",
                        "parameters":[{
                            "type":"image",
                            "image":{
                                "link":ASSERT_EXPERTS_LOGO_URL
                            }}
                        ]
                    },
                ]
            }}
        
        response=requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
                            headers={
                                "Authorization" :f"Bearer {ACCESS_TOKEN}",
                                "Content-Type":"application/json"
                            },
                            json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"staus":"success"} ,200
    except Exception as e:
        logger.critical(f"failed to send help template in eng:{e}")
        raise e
def sending_help_template_in_telugu( recipient_id):
    try:
        logger.debug("sending help template in telugu")
        template_names=whatsapp_template_names()
        help_temp_name=template_names.get("help_template_in_telugu")
        payload={
            "messaging_product":"whatsapp",
            "to":recipient_id,
            "type":"template",
            "template":{
                "name":help_temp_name,
                "language":{
                    "code":"te"
                },
                "components":[
                    {
                        "type":"header",
                        "parameters":[{
                            "type":"image",
                            "image":{
                                "link":ASSERT_EXPERTS_LOGO_URL
                            }}
                        ]
                    },
                ]
            }}
        
        response=requests.post(f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
                            headers={
                                "Authorization" :f"Bearer {ACCESS_TOKEN}",
                                "Content-Type":"application/json"
                            },
                            json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"},200 
    except Exception as e:
        logger.critical(f"failed to send help template in telugu:{e}")
        return {"status":"fail","message":"Internal Error"},500

def send_flow_in_english(recipient_id,user_existence):
    try:
        logger.debug("sending flow in english")
        flow_creditinals=whatsapp_template_names()
        flow_id=flow_creditinals["register_areas_flow_in_eng"].get("flow_id")
        flow_token=flow_creditinals["register_areas_flow_in_eng"].get("flow_token")
        flow_token_wt_ph_num =f"{flow_token}|{recipient_id}|0|{user_existence}"
        payload = {
            "recipient_type": "individual",
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "header": {
                    "type": "text",
                    "text": "Premium Assets"
                },
                "body": {
                    "text": "Please choose interestedt areas"
                },
                "footer": {
                    "text": "Powered by Assert Experts"
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_token": flow_token_wt_ph_num,
                        "flow_id": flow_id,
                        "flow_cta": "select",
                        "flow_action": "data_exchange"
                    }
                }
            }
        }
        response = requests.post(
            f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
    except Exception as e:
        logger.critical(f"failed send flow in english:{e}")
        raise e
def send_flow_in_telugu(recipient_id,user_existence):
    try:
        logger.debug("sending flow in telugu")
        flow_creditinals=whatsapp_template_names()
        flow_id=flow_creditinals["register_areas_flow_in_tel"].get("flow_id")
        flow_token=flow_creditinals["register_areas_flow_in_tel"].get("flow_token")
        flow_token_wt_ph_num =f"{flow_token}|{recipient_id}|1|{user_existence}"
        payload = {
            "recipient_type": "individual",
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "header": {
                    "type": "text",
                    "text": "Assets Experts"
                },
                "body": {
                    "text": "Please choose interestedt areas"
                },
                "footer": {
                    "text": "Powered by Assert Experts"
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_token": flow_token_wt_ph_num,
                        "flow_id": flow_id,
                        "flow_cta": "select",
                        "flow_action": "data_exchange"
                    }
                }
            }
        }
        response = requests.post(
            f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages",
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
    except Exception as e:
        logger.critical("failed send flow in telugu")
        raise e
def send_payment_flow(recipient_id):
    try:
        logger.debug("sending payment flow ")
        flow_creditinals=whatsapp_template_names()
        flow_id=flow_creditinals["payment_flow"].get("flow_id")
        flow_token=flow_creditinals["payment_flow"].get("flow_token")
        payload = {
            "recipient_type": "individual",
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "header": {
                    "type": "image",
                    "image":{
                        "link": ASSERT_EXPERTS_LOGO_URL
                    }
                },
                "body": {
                    "text": "*Choose your subscription plan to receive property notifications on WhatsApp*\nFor any queries, call or whatsapp: *📞8143268869*"
                },
                # "footer": {
                #     "text": "Powered by YourService"
                # },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_token":flow_token,
                        "flow_id":flow_id,
                        "flow_cta": "Proceed",
                        "flow_action": "data_exchange",
                    }
                }
            }
        }
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f'https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages',
            headers=headers,
            json=payload
        )
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)

        return {"status":"success"},200
    except Exception as e:
        logger.critical("failed to send payment flow:{e}")
        raise e
    
def send_recent_property_flow(recipient_id,is_telugu):
    try:
        logger.debug("sending payment flow ")
        flow_creditinals=whatsapp_template_names()
        flow_id=flow_creditinals["get_recent_properties_flow"].get("flow_id")
        flow_token=flow_creditinals["get_recent_properties_flow"].get("flow_token")
        flow_token_wt_ph_num =f"{flow_token}|{recipient_id}"
        messages=whatsapp_message_to_inform_them_to_register()
        if is_telugu:
            body_message=messages.get("message_in_tel_for_flow")
        else:
            body_message=messages.get("message_in_eng_for_flow")
        payload = {
            "recipient_type": "individual",
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "interactive",
            "interactive": {
                "type": "flow",
                "header": {
                    "type": "text",
                    "text": "Assets Experts"
                },
                "body": {
                    "text": body_message
                },
                "footer": {
                    "text": "Powered by Assert Experts"
                },
                "action": {
                    "name": "flow",
                    "parameters": {
                        "flow_message_version": "3",
                        "flow_token":flow_token_wt_ph_num,
                        "flow_id":flow_id,
                        "flow_cta": "Proceed",
                        "flow_action": "data_exchange",
                    }
                }
            }
        }
        headers = {
            'Authorization': f'Bearer {ACCESS_TOKEN}',
            'Content-Type': 'application/json'
        }

        response = requests.post(
            f'https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages',
            headers=headers,
            json=payload
        )
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)

        return {"status":"success"},200
    except Exception as e:
        logger.critical("failed to send payment flow:{e}")
        raise e
    
def send_message_for_order_confirmation(recipent_ph_num,plan,fare,user_name,from_date,to_date):
    try:
        logger.debug("sending message_for_order_confirmation")
        
        if user_name is None:
            user_name="user"
        # message=f"*Subject: Order Confirmation - Thank You for Your Purchase!*\n\n Dear *{user_name}*,\n\nThank you for your recent order with *Assert Experts*! We are pleased to confirm that we have received your order\n*Order Details*:\nPlan Type:*{plan}*\nFee:*{fare}*\n\nBest regards,\n*Assert Experts*"
        message=f"Payment Successful!\nDear *{user_name}*,\nWe are pleased to confirm that your recent payment is successful.\nThanks for become a paid member on Asset Experts.\n *Plan Details:*\n Plan Type:*{plan}* \nPeriod: *1 Year ({from_date} to {to_date}*)\nFee: *{fare} RS*.  \n\nCheers!, *Asset Experts* Team"
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipent_ph_num,
            "type": "text",
            "text": {
                "body": message
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
    except Exception as e:
        logger.critical(f"failed to send order confirmation message")
        raise e
def send_message_to_show_user_selected_areas(telugu,recipent_ph_num,areas,user_name,is_areas_exceeded=False):
    try:  
        logger.debug("sending meessage to_show_user_selected_areas")
        if user_name is None:
            user_name="user"
        if telugu:
            area_names=get_area_names_in_telugu(area_ids=areas)
            message=get_message(area_names=area_names,user_name=user_name,telugu=True,is_areas_exceeded=is_areas_exceeded)
        else:
            area_names=get_area_names_in_english(area_ids=areas)
            message=get_message(area_names=area_names,user_name=user_name,telugu=False,is_areas_exceeded=is_areas_exceeded)
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipent_ph_num,
            "type": "text",
            "text": {
                "body": message
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"},200
    except Exception as e:
        logger.critical(f"failed to send intrsted areas message")
        raise e
    
def send_whatsapp_message(recipent_ph_num,message_to_send):
    try:  
        logger.debug("sending meessage to_inform_user_to_register_areas")
        # messages=whatsapp_message_to_inform_them_to_register()
        # if telugu:
        #     message_to_send=messages.get("message_in_tel")
        # else:
        #     message_to_send=messages.get("message_in_eng")
        logger.debug(f"message:{message_to_send}")
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipent_ph_num,
            "type": "text",
            "text": {
                "body": message_to_send
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"},200
    except Exception as e:
        logger.critical(f"failed to send intrsted areas message")
        raise e
    
    
def get_area_id_for_area_name(area_name,session):
    try:
        logger.debug(f"area name {area_name}")
        query=select(Area).where(Area.name==area_name)
        area_obj=session.execute(query).scalar()
        return area_obj
    except Exception as e:
        raise e
        
    
def send_recent_properties_for_selected_area(recipent_id,selected_area,user_obj):
    try:
        with get_session() as session:
            logger.debug(f"sending recent properties to {recipent_id} for {selected_area}")
            if not user_obj:
                logger.debug("new user")
                logger.debug("sending the language template")
                return send_langauge_selection_template(user_phone_number=recipent_id)
            prefered_langauge=user_obj.prefered_langauge
            area_obj=get_area_id_for_area_name(area_name=selected_area,session=session)
            if not area_obj:
                logger.critical(f"area_bj is not exist for selected area {selected_area} to sent recent properties")
                return {"status":"fail"}
            area_id=area_obj.id
            logger.debug(f"user preferd langauge:{prefered_langauge}")
            logger.debug(f"area_id:{area_id}")
            user_params={"ph_num":[{"ph_num":recipent_id,"langauge":prefered_langauge}],"area_id":area_id}
            query_to_get_properties=select(Property).where(and_(Property.village==selected_area,Property.v_status==True,Property.status=="active")).limit(NUMBER_OF_PROPERTIES_TO_SEND_FOR_RECENT_PROPERTIES_REQUEST)
            prop_objs=session.execute(query_to_get_properties).scalars().all()
            logger.debug(f"propty objects :{prop_objs}")
            count_of_properties=len(prop_objs)
            logger.debug(f"total number of properties:{count_of_properties}")
            area_name_in_tel=" "
            for prop_obj in prop_objs:
                res_params=send_whatsapp_notifications_to_single_user(prop_obj=prop_obj,params=user_params)
                area_name_in_tel=res_params.get("area_name_in_tel"," ")
            is_telugu=prefered_langauge=="Telugu"
            logger.debug(f"user_preferrd_langauge:{is_telugu}")
            messages=whatsapp_message_to_inform_them_to_register()
            if count_of_properties>0:
                if is_telugu:
                    message_to_send=messages.get("message_in_tel_to_vist_web")
                    message_to_send+=f"\n{area_name_in_tel} లో కొత్తగా రిజిస్టర్ అయిన {count_of_properties} ప్రోపర్టీలు 👇🏽"
                else:
                    message_to_send=messages.get("message_in_eng_to_vist_web")
                    message_to_send+=f"\nThe {count_of_properties} most recent properties in {selected_area} are 👇🏽"
                send_whatsapp_message(recipent_ph_num=recipent_id,message_to_send=message_to_send)
            else:
                if is_telugu:
                    message_to_send=messages.get("message_in_tel_for_no_property")
                else:
                    message_to_send=messages.get("message_in_eng_for_no_property")
                send_whatsapp_message(recipent_ph_num=recipent_id,message_to_send=message_to_send)
    except SQLAlchemyError as se:
        raise se
    except Exception as e:
        raise e
    
    
def send_message_to_mediator(recipent_ph_num,message_to_send):
    try:
        logger.debug("sending message_to_mediator")
        message=message_to_send
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID_FOR_WHATSAPP}/messages"
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": recipent_ph_num,
            "type": "text",
            "text": {
                "body": message
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        logger.debug("Request Headers: %s", response.request.headers)
        logger.debug("Request Payload: %s", response.request.body)
        logger.debug("Response Status Code: %s", response.status_code)
        logger.debug("Response Text: %s", response.text)
        return {"status":"success"}
    except Exception as e:
        logger.critical(f"failed to send message to the mediator {recipent_ph_num}")
        raise e