"""Router for nangurepo api"""
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
import json
import string
import random
import os.path
from difflib import get_close_matches
from flask import request, jsonify, Flask
from scraper import get_assignments
import scraper_v2

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
with open("values.json", "r", encoding="UTF-8") as file:
    values = json.load(file)

@app.route('/', methods=['GET'])
def home():
    """The homepage"""
    return jsonify({"Routes available": ["/v1/scrape", "/v2/scrape", "/v2/dvd", "/v2/assassin"]})

def json_response(data):
    """Returns a json response"""
    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def generate_share_code():
    """generates a string of random letters and numbers"""
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
    if os.path.exists(f'dvd_data/{code}.json'):
        code = generate_share_code()
    return code

@app.route('/v2/dvd', methods=['GET'])
def dvd():
    """Function to generate and read share codes"""
    if 'data' in request.args:
        code = generate_share_code()
        with open(f'dvd_data/{code}.json', 'w', encoding="UTF-8") as codefile:
            try:
                json.dump(json.loads(request.args['data']), codefile)
            except json.decoder.JSONDecodeError:
                return json_response({"errors": ["Please provide valid JSON"]})
        return json_response(code)
    if 'code' in request.args:
        if not os.path.exists(f'dvd_data/{request.args["code"]}.json'):
            return json_response({"errors": [f"Share code {request.args['code']} does not exist."]})
        with open(f'dvd_data/{request.args["code"]}.json', 'r', encoding="UTF-8") as codefile:
            try:
                return json_response(json.load(codefile))
            except json.decoder.JSONDecodeError:
                return json_response({"errors": ["Invalid data on file"]})
    return json_response(
        "Either generate a share code using data keyword, or read a share code using the code keyword."
    )

@app.route('/v2/assassin', methods=['GET'])
def assassin():
    """Route to access assassin api"""
    if 'code' in request.args:
        file_name = f'inventories/{request.args["code"]}.json'
        try:
            with open(file_name, "r", encoding="UTF-8") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            with open(file_name, "w", encoding="UTF-8") as data_file:
                json.dump([], data_file)
            with open(file_name, "r", encoding="UTF-8") as data_file:
                data = json.load(data_file)
        if 'name' in request.args:
            try:
                data = request.args["name"].replace(" ", "_").title().split(',')
                data.sort(
                    reverse=True,
                    key=lambda x: values[x.upper().replace("_", " ")]['EXOTICVALUE']
                )
                with open(file_name, "w", encoding="UTF-8") as data_file:
                    json.dump(data, data_file)
                response = jsonify("success")
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            except Exception:
                response = jsonify("failure")
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
        else:
            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

    user_input = request.args['name'].upper().replace('_', ' ') if 'name' in request.args else "NOINPUT"
    if user_input in ["NOINPUT", ""]:
        response = jsonify({
            "ERROR": "No input"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    if ',' in user_input:
        knife_names = user_input.split(',')
    else:
        knife_names = get_close_matches(user_input, values.keys())
    knives = []
    for name in knife_names:
        knife = values[name]
        knife["NAME"] = name.title()
        knives.append(knife)
    response = jsonify(knives)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v1/scrape', methods=['GET'])
def scrape():
    """Route to access scraper v1. Outdated!!"""
    args = format_args(dict(request.args))
    if "errors" in args:
        return jsonify(args)

    return jsonify(
        get_assignments(
            args
        )
    )

@app.route('/v2/scrape', methods=['GET'])
def scrape_v2():
    """
    Route to access scraper v2.
    Takes subdomain, username, password, date, groupByAssignment and errorAssignments
    """
    args = format_args(dict(request.args))
    if "errors" in args:
        return jsonify(args)

    viggo = scraper_v2.Viggoscrape()
    viggo.login_data = {
        "username": args['username'],
        "password": args['password']
    }
    viggo.subdomain = args['subdomain']
    viggo.date_selected = args['date']
    viggo.group_by_assignment = bool(int(args['groupByAssignment']))
    viggo.throw_errors_as_assignments = bool(int(args['errorAssignments']))

    data = viggo.get_assignments()
    if args['search'] is not None:
        data = scraper_v2.search(data, args['search'])

    response = jsonify(data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def format_args(args):  # sourcery skip: remove-redundant-if
    """Sanitizes input"""
    error_list = []
    if 'date' not in args:
        args['date'] = None
    if 'errorAssignments' not in args:
        args['errorAssignments'] = "0"
    if 'search' not in args:
        args['search'] = None
    if not args['errorAssignments'].isdigit():
        error_list.append("errorAssignments must be an integer")
    elif int(args['errorAssignments']) not in [0, 1]:
        error_list.append(
            f"""
            Property errorAssignments is not 0 or 1, recieved {args['errorAssignments']} instead
            """
        )
    if 'groupByAssignment' not in args:
        args['groupByAssignment'] = "1"
    if not args['groupByAssignment'].isdigit():
        error_list.append("Property groupByAssignment must be an integer")
    elif int(args['groupByAssignment']) not in [0, 1]:
        error_list.append(
            f"""
            Property groupByAssignment is not 0 or 1, recieved {args['groupByAssignment']} instead
            """
        )
    if 'subdomain' not in args:
        error_list.append("No subdomain provided")
    if 'username' not in args:
        error_list.append("No username provided")
    if 'password' not in args:
        error_list.append("No password provided")
    if error_list:
        return {
            "errors": error_list
        }
    if args['subdomain'] == '':
        return {"errors": ["Subdomain field is empty."]}

    return args

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', debug=True)
# [END gae_flex_quickstart]
