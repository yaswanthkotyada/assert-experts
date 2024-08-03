from sqlmodel import select, delete,text,and_,or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError,NoResultFound
import logging
from sqlmodel import update,delete
from models import User
from models import UserAreaLink,UserStateLink,UserDistrictLink,District,Area
logger=logging.getLogger(__name__)


def add_selected_state(session,user_id,state):
  try:
    logger.debug("adding user selected areas")
    session.execute(text("PRAGMA foreign_keys = ON;"))
    query=UserStateLink(user_id=user_id,state_id=state)
    session.add(query)
    session.commit()
    logger.debug("state added successfully")
    return {"status":"success","message":"state added successfully"},200
  except IntegrityError as ie:
    raise ie
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e

def add_selected_district(session,user_id,district):
  try:
    logger.debug("adding user selected districts")
    session.execute(text("PRAGMA foreign_keys = ON;"))
    query=UserDistrictLink(user_id=user_id,district_id=district)
    session.add(query)
    session.commit()
    logger.debug("district added successfully")
    return {"status":"success","message":"district added successfully"},200
  except IntegrityError as ie:
    raise ie
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e



def get_all_area_ids(session,district):
  try:
    logger.debug("getting all area ids")
    query=select(Area.id).where(Area.district_id==district)
    area_ids=session.execute(query).scalars().all()
    logger.debug(f"area_ids of{district}:{area_ids}")
    return area_ids
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
  
def add_new_area_with_area_name(session,area_name,district_id):
  try:
    logger.debug(f"adding {area_name},{district_id}")
    query=Area(name=area_name,district_id=district_id)
    session.add(query)
    session.commit()
    area_id=query.id
    return area_id
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
  
def add_new_district_with_name(session,district,state):
  try:
    logger.debug(f"adding new district {district} into db")
    district_query=District(id=district,name=district,state_id=state)
    session.add(district_query)
    logger.debug(f"{district} added into db")
    area_query_for_all_districts=Area(name="All Areas",district_id=district)
    session.add(area_query_for_all_districts)
    session.commit()
    logger.debug("district added successfully")
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
  
def add_selected_area(session,user_id,district_id,area_id,action=False):
  try:
    logger.debug("adding selected areas")
    session.execute(text("PRAGMA foreign_keys = ON;"))
    if action==True:
      area_ids=get_all_area_ids(session=session,district=district_id)
      logger.debug(f"deleting remaining areas of user:{user_id}")
      query=delete(UserAreaLink).where(UserAreaLink.user_id==user_id,UserAreaLink.area_id.in_(area_ids))
      session.execute(query)
      session.commit()      
      logger.debug("deleted successfully")
    query=UserAreaLink(user_id=user_id,area_id=area_id)
    session.add(query)
    session.commit()
    logger.debug(f"area {area_id} added successfully")
    return area_id
  except IntegrityError as ie:
    raise ie
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e

def delete_user_interested_areas(session,user_id,area_id):
  try:
    logger.debug("deleting user selected areas")
    query=delete(UserAreaLink).where(and_(UserAreaLink.user_id==user_id,UserAreaLink.area_id==area_id))
    session.execute(query)
    session.commit()
    logger.debug(f"area_id {area_id} deleted successfully")
    return {"status":"success","message":"area deleted successfully"}
  except IntegrityError as ie:
    raise ie
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
    
def delete_user_interested_districts(session,user_id,district_id):
  try:
    logger.debug("deleting user selected districts")
    query=delete(UserDistrictLink).where((UserDistrictLink.user_id==user_id)&(UserDistrictLink.district_id==district_id))
    session.execute(query)
    session.commit()
    logger.debug("district deleted successfully")
    return {"status":"success","message":"area deleted successfully"}
  except IntegrityError as ie:
    raise ie
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e


def delete_user_interested_states(session,user_id,state_id):
  try:
    logger.debug("deleting user selected states")
    query=delete(UserStateLink).where((UserStateLink.user_id==user_id)&(UserStateLink.state_id==state_id))
    session.execute(query)
    session.commit()
    logger.debug("state deleted successfully")
    return {"status":"success","message":"area deleted successfully"}
  except IntegrityError as ie:
    raise ie
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e

def get_all_existing_districts(session):
  try:
    logger.debug("getting all existing districts")
    query=select(District.id)
    all_districts=session.execute(query).scalars().all()
    logger.debug(f"all districts:{all_districts}")
    return all_districts
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e

def get_all_area_names(session):
  try:
    logger.debug("getting all area names")
    query=select(Area.name)
    all_areas=session.execute(query).scalars().all()
    logger.debug(f"area:{all_areas}")
    return all_areas
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e


def get_user_registered_areas(user_obj):
  try:
    logger.debug("getting user intersted districts")
    registered_area_ids=[]
    registered_areas=[]
    user_registeres_areas=user_obj.areas
    for area_obj in user_registeres_areas:
      registered_area_ids.append(area_obj.id)
      registered_areas.append({"id":area_obj.id,"area":area_obj.name,"district":area_obj.district_id})
    logger.debug(f"registered areas:{registered_area_ids}")
    return {"registered_area_ids":registered_area_ids,"registered_areas":registered_areas}

  except NoResultFound as e:
    raise e
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e 

def get_entire_district_id(district_id,session):
  try:
    logger.debug("getting entire district id")
    query=select(Area.id).where(Area.district_id==district_id,Area.name=="All Areas")
    entire_district_id=session.execute(query).scalar()
    logger.debug(f"entire district id for district {district_id}:{entire_district_id}")
    return entire_district_id
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e

def get_district_id(area_id,session):
  try:
    logger.debug(f"getting istrict id for area_id:{area_id}")
    query=select(Area.district_id).where(Area.id==area_id)
    distrcit_id=session.execute(query).scalar()
    logger.debug(f"district id:{distrcit_id}")
    return distrcit_id
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e

def get_user_obj_with_ph_nums(session,ph_num_1,ph_num_2):
  try:
    logger.debug("searching for user profile with phone number")
    query=select(User).where(or_(User.id==ph_num_1,User.id==ph_num_2))
    user_obj=session.execute(query).scalar()
    return user_obj
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
  
def change_user_id_in_areas(session,ph_num,user_id):
  try:
    query_to_update_areas=update(UserAreaLink).where(UserAreaLink.user_id==ph_num).values(user_id=user_id)
    session.execute(query_to_update_areas)
    logging.debug("UserAreaLink updated successfully")
    query_to_update_districts=update(UserDistrictLink).where(UserDistrictLink.user_id==ph_num).values(user_id=user_id)
    session.execute(query_to_update_districts)
    logging.debug("UserDistrictLink updated successfully")
    query_to_update_states=update(UserStateLink).where(UserStateLink.user_id==ph_num).values(user_id=user_id)
    session.execute(query_to_update_states)
    logging.debug("UserStateLink updated successfully")
    session.commit()
    logging.debug("All updates committed successfully")
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
  
def delete_user(session,user_id):
  try:
    logger.debug(f"deleting user {user_id}")
    query=delete(User).where(User.id==user_id)
    session.execute(query)
    session.commit()
    logger.debug(f"deleted successfuly")
  except SQLAlchemyError as se:
    raise se
  except Exception as e:
    raise e
    
  

    

