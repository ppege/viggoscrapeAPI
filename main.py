"""Router for nangurepo api"""

import json
import string
import random
from os import path, remove
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
    return jsonify({
        "Routes available": [
            "/v1/scrape",
            "/v2/scrape",
            "/v2/dvd",
            "/v2/assassin",
            "/v2/whosapp"
        ]
    })


@app.route('/v2/whosapp/matchmaking', methods=['POST'])
def matchmaking():
    """Start conversation with random user on WhosApp"""
    input_data = request.get_json()
    with open("conversations/matchmaking.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    if json_data["available"]:
        if input_data["user"] in json_data["available"]:
            response = jsonify({"status": "usernameTaken"})
        else:
            response = create_connection(
                [input_data["user"], json_data["available"][0]])
    else:
        json_data["available"].append(input_data["user"])
        with open("conversations/matchmaking.json", "w", encoding="UTF-8") as data_file:
            json.dump(json_data, data_file, indent=4)
        response = jsonify({"status": "waiting"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v2/whosapp/addAvailable', methods=['POST'])
def add_available():
    """Add a user to available in order to not match with the other available users"""
    with open("conversations/matchmaking.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    json_data["available"].append(request.get_json()["user"])
    with open("conversations/matchmaking.json", "w", encoding="UTF-8") as data_file:
        json.dump(json_data, data_file, indent=4)
    response = jsonify({"status": "success"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/v2/whosapp/getAvailable', methods=['GET', 'POST'])
def get_available():
    """Returns available matches"""
    with open("conversations/matchmaking.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    response = jsonify(json_data["available"])
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

def create_connection(users: list):
    """Creates a connection between two users"""
    with open(f"conversations/{users[1]}+{users[0]}.json", "w", encoding="UTF-8") as data_file:
        json.dump([], data_file, indent=4)
    with open("conversations/matchmaking.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    json_data["available"].pop(0)
    json_data["active"][users[1]] = f"{users[1]}+{users[0]}"
    with open("conversations/matchmaking.json", "w", encoding="UTF-8") as data_file:
        json.dump(json_data, data_file, indent=4)
    return jsonify({"status": "connected", "connectionName": f"{users[1]}+{users[0]}"})


@app.route('/v2/whosapp/messages', methods=['POST'])
def get_messages():
    """Returns the messages in a conversation"""
    with open(f"conversations/{request.get_json()['id']}.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    response = jsonify(json_data)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v2/whosapp/send', methods=['POST'])
def send_message():
    """Append a new message to a chat log"""
    with open(f"conversations/{request.get_json()['id']}.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    json_data.append(
        {
            "sender": request.get_json()['user'],
            "message": request.get_json()['message']
        }
    )
    with open(f"conversations/{request.get_json()['id']}.json", "w", encoding="UTF-8") as data_file:
        json.dump(json_data, data_file, indent=4)
    response = jsonify("OK")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v2/whosapp/checkConnection', methods=['POST'])
def check_connection():
    """Check whether or not an end user has been found for matchmaking"""
    with open("conversations/matchmaking.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    user = request.get_json()["user"]
    if user in json_data["active"].keys():
        response = jsonify(
            {"status": "connected", "id": json_data["active"][user]})
    else:
        response = jsonify({"status": "waiting"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v2/whosapp/removeAvailability', methods=['POST'])
def remove_availability():
    """Remove a user from the available list"""
    with open("conversations/matchmaking.json", "r", encoding="UTF-8") as data_file:
        json_data = json.load(data_file)
    user = request.get_json()["user"]
    if user in json_data["available"]:
        json_data["available"].remove(user)
        with open("conversations/matchmaking.json", "w", encoding="UTF-8") as data_file:
            json.dump(json_data, data_file, indent=4)
        response = jsonify({"status": "success"})
    else:
        response = jsonify({"status": "failure"}), status.HTTP_404_NOT_FOUND
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def generate_share_code():
    """generates a string of random letters and numbers"""
    code = ''.join(random.choice(string.ascii_uppercase + string.digits)
                   for _ in range(4))
    if path.exists(f'dvd_data/{code}.json'):
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
        if not path.exists(f'dvd_data/{request.args["code"]}.json'):
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


def authenticate(file_name, password):
    """Authenticate the user"""
    with contextlib.suppress(FileNotFoundError):
        with open(file_name, "r", encoding="UTF-8") as data_file:
            loaded_file = json.load(data_file)
        return loaded_file["password"] == bcrypt.hashpw(
            bytes(password, "utf-8"),
            bytes(loaded_file["password"], "utf-8")
        ).decode()
    return True


@app.route('/v2/assassin/verify', methods=['POST'])
def verify():
    """Lets API user verify if password is correct"""
    post_json = request.get_json()
    file_name = f'inventories/{post_json["code"]}.json'
    if authenticate(file_name, post_json["password"]):
        return "authorized", status.HTTP_200_OK
    return "unauthorized", status.HTTP_401_UNAUTHORIZED


@app.route('/v2/assassin/changePassword', methods=['POST'])
def change_password():
    """Lets API user change inventory password; authentication required"""
    post_json = request.get_json()
    file_name = f'inventories/{post_json["code"]}.json'
    if authenticate(file_name, post_json["password"]):
        with open(file_name, "r", encoding="UTF-8") as data_file:
            loaded_file = json.load(data_file)
        salt = bcrypt.gensalt()
        loaded_file["password"] = bcrypt.hashpw(
            bytes(post_json["newPassword"], "utf-8"),
            salt
        ).decode()
        with open(file_name, "w", encoding="UTF-8") as data_file:
            json.dump(loaded_file, data_file, indent=4)
        return "changed", status.HTTP_200_OK
    return "unauthorized", status.HTTP_401_UNAUTHORIZED


@app.route('/v2/assassin/deleteAccount', methods=['POST'])
def delete_account():
    """API endpoint to let users delete their account given authentication"""
    post_json = request.get_json()
    file_name = f'inventories/{post_json["code"]}.json'
    if authenticate(file_name, post_json["password"]):
        remove(file_name)
        return "deleted", status.HTTP_200_OK
    return "unauthorized", status.HTTP_401_UNAUTHORIZED


def get_knife_names(user_input: string):
    """Get the knife names"""
    if ',' in user_input:
        return user_input.split(',')
    return get_close_matches(user_input, values.keys(), int(
        request.args['limit'])) if 'limit' in request.args else get_close_matches(user_input, values.keys())


def get_knives(names: list):
    """Get the stats for specific knives"""
    knives = []
    for name in names:
        knife = values[name]
        knife["name"] = name.title()
        knives.append(knife)
    return knives


def assassin_post(user_request):
    """Handles the assassin function's incoming POST requests"""
    post_json = user_request.get_json()
    file_name = f'inventories/{post_json["code"]}.json'
    data = sort_items(post_json["data"])

    if not authenticate(file_name, data["password"]):
        response = jsonify("authentication failure")
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, status.HTTP_401_UNAUTHORIZED

    if not path.isfile(file_name):
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


def get_inventory(code: string, password: string = None):
    """
    Gets the content of the user's inventory file; if it doesn't exist, allow it to be created
    """
    file_name = f'inventories/{code}.json'
    try:
        with open(file_name, "r", encoding="UTF-8") as data_file:
            data = json.load(data_file)
            if data["meta"]["private"]:
                if not password:
                    return {"items": [], "meta": {"private": True}}
                if not authenticate(file_name, password):
                    return {"items": [], "meta": {"private": True}}
            return data
    except FileNotFoundError:
        return {"items": [], "meta": {"private": False}}


def assassin_get(user_request):
    """Handles the assassin function's incoming GET requests"""
    ass = Assassin.Assassin()
    if 'update' in user_request.args:
        return jsonify(ass.update_values())
    if 'code' in user_request.args:
        data = get_inventory(
            user_request.args["code"],
            user_request.args["password"] if "password" in user_request.args else None
        )
        if 'data' in user_request.args:
            response = jsonify(
                {"status": "error", "exception": "InvalidMethodError"}
            )
            response.headers.add('Access-Control-Allow-Origin', '*')
            return response
        response = jsonify({"items": data["items"], "meta": data["meta"]})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    user_input = user_request.args['name'].upper().replace(
        '_', ' ') if 'name' in user_request.args else "NOINPUT"
    if user_input in ["NOINPUT", ""]:
        response = jsonify({
            "ERROR": "No input"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    response = jsonify(get_knives(get_knife_names(user_input)))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/v2/assassin', methods=['POST', 'GET'])
def assassin():
    """Route to access assassin api"""
    if request.method == 'POST':
        return assassin_post(request)
    return assassin_get(request)


@app.route('/v1/scrape', methods=['GET'])
def scrape():
    """Route to access scraper v1. Outdated!!"""
    args = format_args(dict(request.args))
    return jsonify(args) if "errors" in args else jsonify(
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
    app.run(host='127.0.0.1', debug=True)
