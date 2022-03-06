"""Router for Viggoscrape.xyz"""
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
import os
import json
from difflib import get_close_matches
from flask import render_template, request, jsonify, send_from_directory, Flask
from scraper import get_assignments
import scraper_v2

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

with open("values.json", "r") as file:
    values = json.load(file)

@app.route('/', methods=['GET'])
def home():
    """The homepage"""
    return jsonify({"Routes available": ["/v1/scrape", "/v2/scrape", "/v2/assassin"]})

@app.route('/v2/assassin', methods=['GET'])
def assassin():
    if 'code' in request.args:
        file_name = f'inventories/{request.args["code"]}.json'
        try:
            with open(file_name, "r") as file:
                data = json.load(file)
        except FileNotFoundError:
            with open(file_name, "w") as file:
                json.dump([], file)
            with open(file_name, "r") as file:
                data = json.load(file)
        if 'name' in request.args:
            try:
                data = request.args["name"].replace(" ", "_").title().split(',')
                with open(file_name, "w") as file:
                    json.dump(data, file)
                response = jsonify("success")
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
            except:
                response = jsonify("failure")
                response.headers.add('Access-Control-Allow-Origin', '*')
                return response
        else:
            response = jsonify(data)
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response

    input = request.args['name'].upper().replace('_', ' ') if 'name' in request.args else "NOINPUT"
    if input in ["NOINPUT", ""]:
        response = jsonify({
            "ERROR": "No input"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    if ',' in input:
        knifeNames = input.split(',')
    else:
        knifeNames = get_close_matches(input, values.keys())
    knives = []
    for name in knifeNames:
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
    Takes subdomain, username, password, date, and groupByAssignment
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

    response = jsonify(
        viggo.get_assignments()
    )
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def format_args(args):  # sourcery skip: remove-redundant-if
    """Sanitizes input"""
    error_list = []
    if 'date' not in args:
        args['date'] = None
    if 'groupByAssignment' not in args:
        args['groupByAssignment'] = "1"
    if not args['groupByAssignment'].isdigit():
        error_list.append("Property groupByAssignment is not an integer")
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
    app.run(host='127.0.0.1')
# [END gae_flex_quickstart]
