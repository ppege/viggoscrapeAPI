from app import app
from scraper import get_assignments

@app.route('/', methods=['GET'])
def home():
    return app.render_template('landing.html')

@app.route('/api/v1/scrape', methods=['GET'])
def scrape():
    error_list = []
    if 'subdomain' not in app.request.args:
        error_list.append("No subdomain provided")
    if 'username' not in app.request.args:
        error_list.append("No username provided")
    if 'password' not in app.request.args:
        error_list.append("No password provided")
    if error_list != []:
        errors = "<br>".join(error_list)
        return f"Error(s) ocurred:<br>{errors}"

    
    return app.jsonify(
        get_assignments(
            app.request.args['subdomain'],
            {
                "USERNAME": app.request.args['username'],
                "PASSWORD": app.request.args['password']
            }
        )
    )
