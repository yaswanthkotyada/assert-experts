from flask import Blueprint, request
from sqlalchemy.exc import SQLAlchemyError
import logging
from flask_restful import Api, Resource
from session import get_session
from crud import get_home_page_properties,get_count_of_plots_flats

home_page_bp = Blueprint("home_page", __name__)

api = Api(home_page_bp)
logger=logging.getLogger(__name__)

class Home_Page(Resource):
    def get(self):
        try:
            logger.debug("getting home page properties")
            offset = int(request.args.get("offset", 0))
            status=request.args.get("status",False)  #condition to show count of flats,plots
            logger.info(f"requested offset value:{offset} ,status:{status}")
            with get_session() as session:
                data = get_home_page_properties(listing_type="buy",
                                                session=session,
                                                offset=offset)
                prop_objs_buy = data["prop_objs"]
                data = get_home_page_properties(listing_type="sell",
                                                session=session,
                                                offset=offset)
                logger.debug("processing the fetched data")
                prop_objs_sell = data["prop_objs"]
                all_buy_properties = []
                for prop_obj in prop_objs_buy:
                    prop_image = []
                    for img_obj in prop_obj.all_prop_imgs:
                        if img_obj:
                            prop_image.append(img_obj.img_url)    
                        break
                    property = {
                        "landmark": prop_obj.landmark,
                        "district": prop_obj.district,
                        "listing_type": prop_obj.listing_type,
                        "property_name":prop_obj.prop_name,
                        "bhk":prop_obj.bhk,
                        "unit": prop_obj.unit,
                        "area": prop_obj.size,
                        "unit_price": prop_obj.price,
                        "prop_type": prop_obj.p_type,
                        "prop_images": prop_image,
                        "p_id": prop_obj.p_id,
                        "p_created_on": str(prop_obj.p_created_on)
                    }
                    all_buy_properties.append(property)
                all_sell_properties = []
                for prop_obj in prop_objs_sell:
                    prop_image = []
                    for img_objs in prop_obj.all_prop_imgs:
                        if img_objs:
                            prop_image.append(img_objs.img_url)
                        break
                    property = {
                        "landmark": prop_obj.landmark,
                        "district": prop_obj.district,
                        "listing_type": prop_obj.listing_type,
                        "property_name":prop_obj.prop_name,
                        "bhk":prop_obj.bhk,
                        "unit": prop_obj.unit,
                        "area": prop_obj.size,
                        "unit_price": prop_obj.price,
                        "prop_type": prop_obj.p_type,
                        "p_id": prop_obj.p_id,
                        "p_created_on": str(prop_obj.p_created_on),
                        "prop_images": prop_image
                    }
                    all_sell_properties.append(property)
                property_type_count={}
                if status:
                    plot_and_flats_count=get_count_of_plots_flats(session=session)
                    property_type_count={
                        "plots_count":plot_and_flats_count["plots_count"],
                        "flats_count":plot_and_flats_count["flats_count"],
                        "commercial_count":plot_and_flats_count["commercial_count"],
                        "agricultural_count":plot_and_flats_count["agricultural_count"]
                    }
                logger.debug(f"count of differnt types of properties:{property_type_count}")
                return {
                    "status": "success",
                    "message": "property fetched successfully",
                    "property": {
                        "sell_properties": all_sell_properties,
                        "buy_properties": all_buy_properties
                    },
                    "property_type_count":property_type_count
                },200
        except SQLAlchemyError as se:
            logger.error(f"sqlalchemy error occured while fetching home page properties:{se}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(
                f"exception occured while fetching home page properties:{e}")
            return {"status":"fail","message": f"Internall Error"}, 500


api.add_resource(Home_Page, '/home')
