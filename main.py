import logging
import datetime
from flask import Flask
from configure import configure_upload_folder
from user import user_bp
from property_images import prop_img_bp
from property import property_bp
from search import search_bp
from price_history import price_hist_bp
from home_page import home_page_bp
from individual_prop import individual_prop_bp
from flask_cors import CORS
from webhook import webhook_bp
from register_areas_flow import register_areas_flow_bp
from payment_flow import payment_flow_bp
from get_recent_properties_flow import get_recent_properties_flow_bp
from support_team import sp_team_bp
from user_interested_areas import user_interested_areas_bp
from subscrption_plan import subscrption_plan_bp
from search_interested_users import search_interested_users_bp
from get_files import get_files_bp
from user_search import user_search_bp

current_date = datetime.datetime.now().strftime("%Y-%m-%d")
log_file_path = f"logs/{current_date}.log"


logging.basicConfig(filename=log_file_path, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder="files", static_url_path='/files')




# CORS(app, resources={r"/*": {"origins": "*"}}, methods=["GET", "POST", "PUT"])

CORS(app)

@app.route('/')
def home():
    return "Welecome to Assert Experts"


with app.app_context():
    configure_upload_folder()

app.register_blueprint(user_bp)
app.register_blueprint(prop_img_bp)
app.register_blueprint(property_bp)
app.register_blueprint(search_bp)
app.register_blueprint(price_hist_bp)
app.register_blueprint(home_page_bp)
app.register_blueprint(individual_prop_bp)
app.register_blueprint(webhook_bp)
app.register_blueprint(register_areas_flow_bp)
app.register_blueprint(payment_flow_bp)
app.register_blueprint(get_recent_properties_flow_bp)
app.register_blueprint(subscrption_plan_bp)
app.register_blueprint(search_interested_users_bp)
app.register_blueprint(sp_team_bp)
app.register_blueprint(user_interested_areas_bp)
app.register_blueprint(get_files_bp)
app.register_blueprint(user_search_bp)



if __name__ == "__main__":
    app.run(debug=True, port=8080)
