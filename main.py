from scraper import get_assignments
from flask import render_template, request, jsonify, send_from_directory, Flask
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('landing.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                                'favicon.ico', mimetype='image/vnc.microsoft.icon')

@app.route('/api/v1/scrape', methods=['GET'])
def scrape():
    error_list = []
    if 'subdomain' not in request.args:
        error_list.append("No subdomain provided")
    if 'username' not in request.args:
        error_list.append("No username provided")
    if 'password' not in request.args:
        error_list.append("No password provided")
    if error_list != []:
        errors = "<br>".join(error_list)
        return f"Error(s) ocurred:<br>{errors}"

    
    return jsonify(
        get_assignments(
            request.args['subdomain'],
            {
                "USERNAME": request.args['username'],
                "PASSWORD": request.args['password']
            }
        )
    )

app.run(debug=True)