# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_flex_quickstart]
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

@app.route('/placeholder')
def placeholder():
    return render_template('placeholder.html')

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
        errors = {
            "errors": error_list
        }
        return jsonify(errors)
    if request.args['subdomain'] == '':
        return jsonify("Subdomain field is empty.")

    return jsonify(
        get_assignments(
            request.args
        )
    )

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_flex_quickstart]
