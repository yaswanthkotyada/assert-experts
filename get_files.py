from flask import  Blueprint
from flask_restful import Api, Resource
import json
import logging
from flask import send_file
from sqlmodel import select
from models import District, State
from sqlalchemy.exc import  SQLAlchemyError
from session import get_session
from crud import  read_json_file

logger=logging.getLogger(__name__)
get_files_bp = Blueprint("get_files", __name__)
api = Api(get_files_bp)
premium_assests_json = "premium_assets.json"


class Get_Supported_Areas_File(Resource):
    def get(self):
        try:
            logger.info("getting supported areas")
            dict = {}
            districts_in_data_base = []
            state_status=[]
            with get_session() as session:
                query = select(District)
                district_objs = session.execute(query).scalars().all()
                if not district_objs:
                    logger.warning("districts are not exist in the data base")
                    raise ValueError("districts not existed in the data base")
                for district_obj in district_objs:
                    district_name = district_obj.id
                    dict[district_name] = []
                    districts_in_data_base.append(district_name)
                    for area_obj in district_obj.areas:
                        dict[district_name].append({"id":area_obj.id,"area":area_obj.name})
                query_to_state_objs=select(State)
                state_objs=session.execute(query_to_state_objs).scalars().all()
                for state_obj in state_objs:
                    if len(state_obj.districts)>0:
                        state_status.append({"state":state_obj.name,"status":True})
                    else:
                        state_status.append({"state":state_obj.name,"status":False})
            districts_file = read_json_file(premium_assests_json)
            for state in districts_file:
                for district in districts_file[state]:
                    if district in districts_in_data_base:
                        districts_file[state][district] = True
            res_data = {"areas": dict, "district_status": districts_file,"state_status":state_status}
            logger.debug(f"supporting_areas:{res_data}")
            with open('areas_supporting.json', 'w') as file:
                json.dump(res_data, file, indent=4)
            logger.info("sending file")
            return send_file('areas_supporting.json', as_attachment=True)

        except SQLAlchemyError as se:
            logger.error(f"sqlalchemy error occured while loading data into file:{se}")
            return {"status":"fail","message":"Server Error"},500
        except Exception as e:
            logger.critical(f"exception occured while fetching home page properties:{e}")
            return {"status":"fail","message": f"Internall Error"}, 500

api.add_resource(Get_Supported_Areas_File, '/getfile')


