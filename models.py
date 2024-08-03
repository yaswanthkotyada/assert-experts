
from typing import Optional, List
from sqlmodel import SQLModel, Field, Column, create_engine, Integer, ForeignKey, Relationship, String
from datetime import datetime, timezone
from sqlalchemy import Index



engine = create_engine('sqlite:///premiumassests1.db')



class UserAreaLink(SQLModel, table=True):
    user_id: Optional[str] = Field(default=None,
                                   foreign_key="user.id",
                                   primary_key=True)
    area_id: Optional[int] = Field(default=None,
                                   foreign_key="area.id",
                                   primary_key=True)


class UserDistrictLink(SQLModel, table=True):
    user_id: Optional[str] = Field(default=None,
                                   foreign_key="user.id",
                                   primary_key=True)
    district_id: Optional[int] = Field(default=None,
                                       foreign_key="district.id",
                                       primary_key=True)





class UserStateLink(SQLModel, table=True):
    user_id: Optional[str] = Field(default=None,
                                   foreign_key="user.id",
                                   primary_key=True)
    state_id: Optional[str] = Field(default=None,
                                    foreign_key="state.id",
                                    primary_key=True)


class User(SQLModel, table=True):
    __tablename__ = "user"
    id: Optional[str] = Field(sa_column=Column(String, primary_key=True))
    name: Optional[str] = Field(default=None)
    role: str = Field(default="user")
    updated_by: Optional[str] = Field(default=None, sa_column=Column(String))
    created_on: datetime = Field(default=datetime.now(timezone.utc))
    updated_on: datetime = Field(default=datetime.now(timezone.utc))
    email: Optional[str] = Field(default=None)
    comments: Optional[str] = Field(default=None)
    requirements: Optional[str] = Field(default=None)
    ph_num_1: Optional[int] = Field(default=None)
    ph_num_2: Optional[int] = Field(default=None)
    profession: Optional[str] = Field(default=None)
    prefered_langauge:Optional[str]=Field(default="English")
    address: Optional[str] = Field(default=None)
    active_notifications: Optional[int] = Field(default=0)
    num_of_notifications_notified:Optional[int]=Field(default=0)
    status:Optional[str]=Field(default="active")
    is_whatsapp_user:Optional[bool]=Field(default=False)
    payments: List["Payment"] = Relationship(back_populates="user",sa_relationship_kwargs={"foreign_keys": "Payment.u_id"})
    areas: List["Area"] = Relationship(back_populates="users",
                                       link_model=UserAreaLink)
    districts: List["District"] = Relationship(back_populates="users",
                                               link_model=UserDistrictLink)
    states: List["State"] = Relationship(back_populates="users",
                                         link_model=UserStateLink)
    all_properties: List["Property"] = Relationship(
        back_populates="user_instance",
        sa_relationship_kwargs={"foreign_keys": "Property.cont_user_id"})
    __table_args__ = (
        Index('idx_user_id', 'id'),
        Index('idx_ph_num_1', 'ph_num_1'),
        Index('idx_ph_num_2', 'ph_num_2'),
    )


class Property(SQLModel, table=True):
    __tablename__ = "property"
    p_id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True))
    cont_user_id: Optional[str] = Field(default=None,
                                        sa_column=Column(
                                            String, ForeignKey("user.id")))
    prop_name: Optional[str] = Field(default=None)
    listing_type: Optional[str] = Field(default=None)
    bhk:Optional[str]=Field(default=None)
    p_type: Optional[str] = Field(default=None) 
    size: Optional[float] = Field(default=0)
    unit: Optional[str] = Field(default=None)
    price: Optional[float] = Field(default=0)
    dimensions: Optional[str] = Field(default=None)
    survey_number: Optional[str] = Field(default=None)
    doc_num: Optional[str] = Field(default=None)
    direction: Optional[str] = Field(default=None)
    est_year: Optional[int] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    state: Optional[str] = Field(default=None)
    district: Optional[str] = Field(default=None)
    village: Optional[str] = Field(default=None)
    landmark: Optional[str] = Field(default=None)
    ad_info: Optional[str] = Field(default=None)
    comments: Optional[str] = Field(default=None)
    disputes: Optional[str] = Field(default=None)
    developments: Optional[str] = Field(default=None)
    #reigster location
    reg_loc: Optional[str] = Field(default=None)
    med_name: Optional[str] = Field(default=None)
    med_num1: Optional[int] = Field(default=None)
    med_num2: Optional[int] = Field(default=None)
    own_name: Optional[str] = Field(default=None)
    own_num1: Optional[int] = Field(default=None)
    own_num2: Optional[int] = Field(default=None)
    parking: Optional[bool] = Field(default=None)
    approved_by: Optional[str] = Field(default=None)
    docFile: Optional[str] = Field(default=None)
    loan_eligible: Optional[bool] = Field(default=False)
    status: Optional[str ]= Field(default="new")
    bound_wall: Optional[str] = Field(default="availble")
    furnshied: Optional[str] = Field(default="no")
    lift: Optional[str] = Field(default='no')
    rera: Optional[str] = Field(default="no")
    num_open_sides: Optional[str] = Field(default=None)
    v_status: Optional[bool] = Field(default=False)
    v_comments: Optional[str] = Field(default=None)
    rating: Optional[int] = Field(default=None)
    notified: Optional[bool] = Field(default=False)
    num_of_times_notified: Optional[int] = Field(default=0)
    num_of_leads:Optional[int]=Field(default=0)
    govt_price: Optional[float] = Field(default=None)
    updated_by: Optional[str] = Field(default=None, sa_column=Column(String))
    p_created_on: datetime = Field(default=datetime.now(timezone.utc))
    p_updated_on: datetime = Field(default=datetime.now(timezone.utc))
    supp_requests: List["SupportRequest1"] = Relationship(
        back_populates="req_property",
        sa_relationship_kwargs={"foreign_keys": "SupportRequest1.prop_id"})
    user_instance: Optional[User] = Relationship(
        back_populates="all_properties")
    all_prop_imgs: List["Property_img"] = Relationship(
        back_populates="property_instance",
        sa_relationship_kwargs={"foreign_keys": "Property_img.prop_id"})
    price_history: List["Propert_Price_History"] = Relationship(
        back_populates="property_inst",
        sa_relationship_kwargs={
            "foreign_keys": "Propert_Price_History.prop_id"
        })
    __table_args__=(Index("idx_p_id","p_id"),
                    Index("idx_property_type","p_type"),)

class Property_img(SQLModel, table=True):
    __tablename__ = "property_img"
    img_id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True))
    prop_id: int = Field(
        sa_column=Column(Integer, ForeignKey("property.p_id")))
    img_url: Optional[str] = Field(default=None)
    property_instance: Optional[Property] = Relationship(
        back_populates="all_prop_imgs")
    status: str = Field(default="not verified")


class Propert_Price_History(SQLModel, table=True):
    id: Optional[int] = Field(sa_column=Column(Integer, primary_key=True))
    prop_id: int = Field(
        sa_column=Column(Integer, ForeignKey("property.p_id")))
    old_price: Optional[float] = Field(default=None)
    updated_on: datetime = Field(default=datetime.now(timezone.utc))
    property_inst: Optional[Property] = Relationship(
        back_populates="price_history")


class State(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    name: str
    users: List[User] = Relationship(back_populates="states",
                                     link_model=UserStateLink)
    districts: List["District"] = Relationship(back_populates="state")


class District(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str
    state_id: Optional[str] = Field(None, foreign_key="state.id")
    users: List[User] = Relationship(back_populates="districts",
                                     link_model=UserDistrictLink)
    state: Optional["State"] = Relationship(back_populates="districts")
    areas: List["Area"] = Relationship(
        back_populates="district",
        sa_relationship_kwargs={"foreign_keys": "Area.district_id"})






class Area(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    district_id: Optional[str] = Field(
        sa_column=Column(ForeignKey("district.id")))
    users: List[User] = Relationship(back_populates="areas",
                                     link_model=UserAreaLink)
    district: Optional["District"] = Relationship(back_populates="areas")
    __table_args__ = (Index('idx_area_name', 'name'),
                      Index("idx_area_id","id"),
                      Index("idx_district_id","district_id"),)

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    u_id: str = Field(default=None, foreign_key="user.id")
    subscription_plan_type: Optional[str] = Field(default=None)
    from_date:Optional[datetime]=Field(default=None)
    to_date:Optional[datetime]=Field(default=None)
    payment_gateway: Optional[str] = Field(default=None)
    price: Optional[float] = Field(default=None)
    payment_date: Optional[datetime] = Field(default=datetime.now(timezone.utc))
    order_id: Optional[str] = Field(default=None)
    transaction_id: Optional[str] = Field(default=None)
    Payment_status: Optional[str] = Field(default="unpaid")
    user: Optional[User] = Relationship(back_populates="payments")
    comments: Optional[str] = Field(default=None)


class SupportRequest1(SQLModel,table=True):
    id:Optional[int]=Field(sa_column=Column(Integer,primary_key=True))
    prop_id:Optional[int]=Field(sa_column=Column(ForeignKey("property.p_id")))
    user_name:Optional[str]=Field(default=None)
    #user ph num
    ph_num:Optional[int]=Field(default=None)
    email:Optional[str]=Field(default=None)
    #requested query 
    req_query:Optional[str]=Field(default=None)
    status:Optional[str]=Field(default='active')
    #request created on
    created_on:datetime=Field(default=datetime.now(timezone.utc))
    location:Optional[str]=Field(default=None)
    property_type:Optional[str]=Field(default=None)
    #staff comments
    s_comments:Optional[str]=Field(default=None)
    req_property:Optional[Property]=Relationship(back_populates="supp_requests")


class WhatsappAds(SQLModel,table=True):
    id:Optional[int]=Field(primary_key=True)
    phone_number:Optional[int]=Field(default=None)
    project_areas:Optional[str]=Field(default=None)
    ad_description:Optional[str]=Field(default=None)
    number_of_notifications:Optional[int]=Field(default=None)
    created_on:datetime=Field(default=datetime.now(timezone.utc))


SQLModel.metadata.create_all(engine)














