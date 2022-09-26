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
import contextlib
from difflib import get_close_matches
import bcrypt
from flask import request, jsonify, Flask
from flask_api import status
from flask_cors import CORS
from scraper import get_assignments
import scraper_v2
import assassin as Assassin

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
CORS(app)
with open("values.json", "r", encoding="UTF-8") as file:
    values = json.load(file)


@app.route('/', methods=['GET'])
def home():
    """The homepage"""
    return jsonify({"Routes available": ["/v1/scrape", "/v2/scrape", "/v2/dvd", "/v2/assassin"]})


def generate_share_code():
    """generates a string of random letters and numbers"""
    code = ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(4))
    if os.path.exists(f'dvd_data/{code}.json'):
        code = generate_share_code()
    return code


@app.route('/v2/postData', methods=['POST'])
def post_data():
    """Function to generate some share codes"""
    code = generate_share_code()
    with open(f'dvd_data/{code}.json', 'w', encoding="UTF-8") as codefile:
        try:
            json.dump(request.get_json(), codefile)
            response = jsonify({"code": code})
        except json.decoder.JSONDecodeError:
            response = jsonify({"error": "Please provide valid JSON"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v2/dvd', methods=['GET', 'POST'])
def dvd():
    """Function to read share codes"""
    if 'code' in request.args:
        if not os.path.exists(f'dvd_data/{request.args["code"]}.json'):
            response = jsonify(
                {"error": f"Share code {request.args['code']} does not exist."})
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        with open(f'dvd_data/{request.args["code"]}.json', 'r', encoding="UTF-8") as codefile:
            try:
                response = jsonify(json.load(codefile))
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            except json.decoder.JSONDecodeError:
                response = jsonify({"error": "Invalid data on file"})
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
    response = jsonify({
        "error":
        "Either generate a share code using data keyword, or read a share code using the code keyword."
    })
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def get_exotic_value(data):
    """Gets exotic values while handling exceptions"""
    try:
        return int(values[data["name"].upper().replace("_", " ")]['exoticvalue'])
    except ValueError:
        return 0

def sort_items(data):
    """Sort the items by value and favorite"""
    data["items"].sort(
        reverse=True,
        key=get_exotic_value
    )
    data["items"].sort(
        key=lambda x: 0 if x["favorite"] else 1
    )
    return data

def authenticate(file_name, data):
    """Authenticate the user"""
    with contextlib.suppress(FileNotFoundError):
        with open(file_name, "r", encoding="UTF-8") as data_file:
            loaded_file = json.load(data_file)
        return loaded_file["password"] == bcrypt.hashpw(
            bytes(data["password"], "utf-8"),
            bytes(loaded_file["password"], "utf-8")
        ).decode()
    return True

@app.route('/v2/assassin', methods=['POST', 'GET'])
def assassin():
    """Route to access assassin api"""
    if request.method == 'POST':
        # try:
        post_json = request.get_json()
        file_name = f'inventories/{post_json["code"]}.json'
        data = sort_items(post_json["data"])

        if not authenticate(file_name, data):
            response = jsonify("authentication failure")
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response, status.HTTP_401_UNAUTHORIZED

        if not os.path.isfile(file_name):
            salt = bcrypt.gensalt()
            data["password"] = bcrypt.hashpw(
                bytes(data["password"], "utf-8"),
                salt
            ).decode()
        else:
            with open(file_name, "r", encoding="UTF-8") as data_file:
                loaded_file = json.load(data_file)
            data["password"] = bcrypt.hashpw(
                bytes(data["password"], "utf-8"),
                bytes(loaded_file["password"], "utf-8")
            ).decode()
        with open(file_name, "w", encoding="UTF-8") as data_file:
            json.dump(data, data_file, indent=4)
        response = jsonify("success")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, status.HTTP_200_OK
        # except Exception as exception:  # pylint: disable=broad-except
        #     response = jsonify(
        #         {"status": "error", "exception": str(exception)})
        #     response.headers.add('Access-Control-Allow-Origin', '*')
        #     return response, status.HTTP_400_BAD_REQUEST
    else:
        ass = Assassin.Assassin()
        if 'update' in request.args:
            return jsonify(ass.update_values())
        if 'code' in request.args:
            file_name = f'inventories/{request.args["code"]}.json'
            try:
                with open(file_name, "r", encoding="UTF-8") as data_file:
                    data = json.load(data_file)
            except FileNotFoundError:
                data = {"items": []}
            if 'data' in request.args:
                response = jsonify(
                    {"status": "error", "exception": "InvalidMethodError"}
                )
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            response = jsonify(data["items"])
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        user_input = request.args['name'].upper().replace(
            '_', ' ') if 'name' in request.args else "NOINPUT"
        if user_input in ["NOINPUT", ""]:
            response = jsonify({
                "ERROR": "No input"
            })
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        if ',' in user_input:
            knife_names = user_input.split(',')
        else:
            knife_names = get_close_matches(user_input, values.keys(), int(
                request.args['limit'])) if 'limit' in request.args else get_close_matches(user_input, values.keys())
        knives = []
        for name in knife_names:
            knife = values[name]
            knife["name"] = name.title()
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
