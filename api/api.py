import re
import flask
from flask import jsonify, request, render_template
from scraper import get_assignments

app = flask.Flask(__name__)
app.config["DEBUG"] = True

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/', methods=['GET'])
def home():
    return render_template('landing.html')

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

app.run()