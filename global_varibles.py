IMAZE_SIZE = 10 * 1024 * 1024
DOCUMENT_SIZE = 10 * 1024 * 1024
PAGE_LIMIT = 40
PROPERTIES_AROUND_KM = 5
COUNT_OF_RECENT_PROPERTIES = 10  # NUMBER OF PROPERTIES TO DISPLAY UNDER THE INDIVIDUAL PROPERTY
NUMBER_OF_AREAS_ALLOWED_FOR_FREE_USER = 10
NUMBER_OF_PROPERTIES_TO_SEND_FOR_RECENT_PROPERTIES_REQUEST=5
OFFICE_NUMBER=8143268869

PLAN_FEES = {
    "classic": {
        "text_for_flow": "500 Rs Per Year",
        "period_in_months": 12,
        "value": 500,
        "number_of_notifications": 500},
    "premium": {
        "text_for_flow": "1000 Rs Per 2 Years",
        "period_in_months": 24,
        "value": 1000,
        "number_of_notifications": 1000}
}

DEFAULT_ADS= [
    "Sell your property swiftly with ASSET EXPERTS! List today for a faster transaction",
    "Ready to move on? List your property on ASSET EXPERTS for a quick and hassle-free sale!",
    "Looking to sell your property? List with ASSET EXPERTS for a seamless selling experience",
    "Turn your property into cash! List with ASSET EXPERTS for a speedy sale",
    "Find your dream property with ASSET EXPERTS! Explore verified listings for your next investment",
    "Searching for the perfect home or investment? Discover top properties with ASSET EXPERTS",
    "Looking to buy property? Get exclusive listings and personalized service with ASSET EXPERTS",
    "Invest wisely! Browse properties with ASSET EXPERTS for lucrative opportunities",
    "Discover V K Aurora in Madhurawada, Visakhapatnam—luxurious 3 BHK apartments starting at ₹68.36 L, just minutes from schools, hospitals, and shopping. Enjoy top-notch amenities in a prime location",
    "Explore Sri Nidhi Orchid in Maddilapalem, Visakhapatnam—spacious 3 BHK apartment for ₹1.15 Cr with stunning beach and hill views. Enjoy zero brokerage, premium amenities, and unbeatable location",
    "Discover MK One in Yendada, Visakhapatnam—luxurious 3 BHK apartments starting at ₹2 Cr in Vizag's tallest iconic project. Enjoy over 151 amenities, spacious units, and prime location near schools, hospitals, and restaurants",
    "Explore Ocean Heights in Yendada, Visakhapatnam—spacious 2 BHK sea-facing apartment for ₹79 L with premium amenities, zero brokerage, and proximity to top schools, hospitals, and restaurants",
    "Experience luxury living at KR Meghana Royal Towers, Pedda Waltair, Visakhapatnam—spacious 4 BHK apartments starting at ₹5.67 Cr. Enjoy 24-hour concierge, top-notch security, and proximity to schools, hospitals, and the airport",
    "Discover Sri Aditya Residency in Lawsons Bay Colony, Visakhapatnam—spacious 3 BHK apartments for ₹1.57 Cr with all modern amenities, including 2 car parkings, a generator, and a community hall. Enjoy a prime location near top schools, hospitals, and restaurants",
    "Explore S D Srinivasa Nilayam in Aganampudi, Visakhapatnam—affordable 3 BHK apartments for ₹47.5 L with 24x7 security, power backup, lift, and close proximity to bus stops, schools, hospitals, and restaurants",
    "Discover Celest by Apex Meadows Pvt. Ltd. in Gajuwaka, Visakhapatnam—a premier gated community offering spacious 2 BHK flats for ₹75 Lac with 823 sq.ft. carpet area",
    "Explore Sardar Nest by Sardar Projects Pvt. Ltd. in Gajwaka Jn., Visakhapatnam—affordable 2 BHK flats available for ₹41.5 Lac with 1185 sq.ft. super built-up area. Enjoy amenities like a swimming pool, gymnasium, clubhouse, and jogging track",
    "Discover MVV Green Field by MVV Builders in Yendada, Visakhapatnam—spacious 2 BHK semi-furnished flats for ₹63.7 Lac with 1158 sq.ft. super built-up area"]
    

DEFAULT_PROPERTY_URLS_FOR_WHATSAPP = {
    "sell": {
        "flat": "https://aebend.varnastudio.in/aebend/files/images/flat_final_2024_07_19_19_51_27.jpeg",
        "plot": "https://aebend.varnastudio.in/aebend/files/images/Plots_final_2024_07_19_19_51_26.jpg",
        "agricultural land":"https://aebend.varnastudio.in/aebend/files/images/agri_cultural_land_final_2024_07_19_20_13_09.jpg",
        "land": "https://aebend.varnastudio.in/aebend/files/images/agri_cultural_land_final_2024_07_19_20_13_09.jpg",
        "pg":"https://aebend.varnastudio.in/aebend/files/images/pg_final_1_2024_07_19_19_51_27.jpeg",
        "office place":"https://aebend.varnastudio.in/aebend/files/images/office_final_1_2024_07_19_19_51_26.jpeg",
        "co working place":"https://aebend.varnastudio.in/aebend/files/images/office_final_1_2024_07_19_19_51_26.jpeg",
        "student hostel":"https://aebend.varnastudio.in/aebend/files/images/pg_final_1_2024_07_19_19_51_27.jpeg",
        "independent house": "https://aebend.varnastudio.in/aebend/files/images/flat_final_2024_07_19_19_51_27.jpeg",
        "commercial":"https://aebend.varnastudio.in/aebend/files/images/agri_cultural_land_final_2024_07_19_20_13_09.jpg"},
    "buy": {
        "flat": "https://aebend.varnastudio.in/aebend/files/images/wanted_flat_2024_07_19_19_51_26.jpg",
        "plot": "https://aebend.varnastudio.in/aebend/files/images/wanted_plots_1_2024_07_19_19_51_26.jpg",
        "agricultural land":"https://aebend.varnastudio.in/aebend/files/images/wanted_land_1_2024_07_19_19_51_27.jpg",
        "land": "https://aebend.varnastudio.in/aebend/files/images/wanted_land_1_2024_07_19_19_51_27.jpg",
        "pg":"https://aebend.varnastudio.in/aebend/files/images/wanted_pg_2024_07_19_19_49_40.jpg",
        "office place":"https://aebend.varnastudio.in/aebend/files/images/wanted_office_2024_07_19_19_51_26.jpg",
        "co working place":"https://aebend.varnastudio.in/aebend/files/images/wanted_office_2024_07_19_19_51_26.jpg",
        "student hostel":"https://aebend.varnastudio.in/aebend/files/images/pg_final_1_2024_07_19_19_51_27.jpeg",
        "independent house": "https://aebend.varnastudio.in/aebend/files/images/wanted_flat_2024_07_19_19_51_26.jpg",
        "commercial":"https://aebend.varnastudio.in/aebend/files/images/wanted_land_1_2024_07_19_19_51_27.jpg"},
    "default": "https://aebend.varnastudio.in/aebend/files/images/Plots_final_2024_07_19_19_51_26.jpg"
}

ACCESS_TOKEN = "EAALjCzKoWQ0BO8ZB8TOzNzct1MYZAo7Lvo2bOfNa6X2GZBwl1ZCkxCO9kYtEwtskrdU23SMZCuOvBaxbZC1MwZBhbtusF9q6aQZAkTYySxbAyLbtyhtjOZBK06z7aO4FnMapXJg1aTNnMSinBZCZA3MgeGJ7UNBiOmGZBfYZCSAAZBcMMZCWZA0KxmMeHfLZCMEGUmdUyfhYVf6bpZCNPztZAxNSlc4"

VERIFY_TOKEN = "EAALjCzKoWQ0BO27lLKeZAlgNL2UGjPSLY4WQaRWo17DJJWo34ekea5Hm6C2nJARhMYLSbsixC0ZApgZCGeLE4KvH1NRvE0dcVuJZCmE9ZADZBI0c3wKiSa9iIC7JK7d7n9Q8DQ3DHnvSoPF5cnpWBnxm6YOfxqseFGtUX5tLMEoDh51bcuuZBJPQHyDxZBVhvFaSrkXZCbI8PB1WwCTSdOQTNXw9qxCmc"
APP_SECRET = "650360684904fb7c6e557fc293ee1a2a"
PRIVATE_KEY_FILE_PASSWORD = b"9848596651"

PHONE_NUMBER_ID_FOR_WHATSAPP = 295831620286293
ASSERT_EXPERTS_LOGO_URL = "https://aa27744c-8ef2-49c6-a5ac-b6385a96c669-00-2x83qwts329l5.pike.replit.dev/images/premium_assests_logo.jpeg"

NUMBER_OF_ALL_AREAS=4
NUMBER_OF_AREAS_IN_A_DISTRICT=5


DEFAULT_PROPERTY_AREAS=[
    {"id":"Akkayyapalem","title":"Akkayyapalem"},
    {"id":"Boyapalem","title":"Boyapalem"},
    {"id":"Bheemunipatnam","title":"Bheemunipatnam"},
    {"id":"Chinnamushidiwada","title":"Chinnamushidiwada"},
    {"id":"Duvada","title":"Duvada"},
    {"id":"Ayyannapeta","title":"Ayyannapeta"},
    {"id":"Badangi","title":"Badangi"},
    {"id":"Balijipeta","title":"Balijipeta"},
    {"id":"Bhogapuram","title":"Bhogapuram"},
    {"id":"Bobbili","title":"Bobbili"},
    {"id":"Bondapalle","title":"Bondapalle"},
    {"id":"Amalapuram","title":"Amalapuram"},
    {"id":"Annavaram","title":"Annavaram"},
    {"id":"Bhadrachalam","title":"Bhadrachalam"},
    {"id":"Chinturu","title":"Chinturu"},
    {"id":"Dakodu","title":"Dakodu"},
    {"id":"Dammapeta","title":"Dammapeta"},
    {"id":"Gellavada","title":"Gellavada"}
]

def whatsapp_template_names():
    template_names = {
        "property_notification_temp_in_telugu": "property_notification_in_telugu",  # langauge should be te
        "property_notification_temp_in_english": "property_notification_in_english",  # langauge should be en
        "register_areas_flow_in_tel": {"flow_token": "flows-builder-30813ed3", "flow_id": "450825414575466"},
        "register_areas_flow_in_eng": {"flow_token": "flows-builder-314f27a3", "flow_id": "1413902105862594"},
        "payment_flow": {"flow_token": "flows-builder-5eacd35a", "flow_id": "342641402230733"},
        "get_recent_properties_flow": {"flow_token": "flows-builder-5cf77fdd", "flow_id": "1036383987851929"},
        "help_template_in_telugu": "help_template_in_telugu",
        "help_template_in_english": "help_temp_in_en",
        "langauge_selection_temp_name": "langauge_selection",
        "interest_property_in_english":"interest_template",
        "temp_to_mediator":"first_message_to_mediator"}
    return template_names



def whatsapp_message_to_inform_them_to_register():
    messages={
        "message_in_eng":"you did not registered any areas yet/n first select your areas of interest",
        'message_in_tel':"మీరు ఇంకా ఏ ప్రాంతాలను నమోదు చేయలేదు/n ముందుగా మీకు ఆసక్తి ఉన్న ప్రాంతాలను ఎంచుకోండి",
        "message_in_eng_for_flow":"Please select your area of interest to get recent listed properties",
        "message_in_tel_for_flow":"ఇటీవలె రిజిస్టర్  అయిన ప్రోపర్టీలు చూడటానికి ఏదైనా ప్రాంతాన్ని ఎంచుకోండి",
        "message_in_eng_for_no_property":"we keep posting you registered properties in this area",
        "message_in_tel_for_no_property":"ఈ ప్రాంతంలో రిజిస్టర్  అయిన ప్రోపర్టీలు మేము మీకు పోస్టు చేస్తాము",
        "message_in_eng_to_vist_web":"For more properties, visit www.assertexperts.com",
        "message_in_tel_to_vist_web":"మరిన్ని ప్రోపర్టీస్ కోసం www.assertexperts.com"
    }
    return messages

