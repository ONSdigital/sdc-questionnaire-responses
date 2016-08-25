import requests
from json import dumps
from decoder import get_json


def get(url, parameters={}, headers={}):
    response = requests.get(url, params=parameters, headers=headers)
    return process(response)


def post(url, json, headers={}):
    headers["Content-Type"] = "application/json"
    response = requests.post(url, data=json, headers=headers)
    return process(response)


def process(response):
    if response.status_code < 400:
        #print(response.status_code)
        return {
            "status": response.status_code,
            "json": response.json()
        }
    else:
        return {
            "status": response.status_code,
            "text": response.text
        }


# Test the authentication / authorisation API

component = "sdc-login-user"
url = "https://" + component + ".herokuapp.com"
# url = "http://localhost:5000"
print(" >>> Logging in and collecting tokens... (" + url + ")")


# Data we're going to work through


# Email address options

# email = "florence.nightingale@example.com"
# email = "chief.boyce@example.com"
email = "fireman.sam@example.com"
# email = "rob.dabank@example.com"


# Internet access code options

access_code = "abc123"
# access_code= "def456"
# access_code= "ghi789"


token = None
respondent_id = None

# Accout login

uri = "/login"
input = {"email": email}
result = post(url + uri, dumps(input))
if result["status"] == 200:
    json = result["json"]
    token = json["token"]
else:
    print("Error: " + str(result["status"]) + " - " + repr(result["text"]))

print(" <<< Token: " + token)


# Respondent units the respondent is associated with

reporting_units = []
uri = "/reporting_units"
result = get(url + uri, headers={"token": token})
if result["status"] == 200:
    json = result["json"]
    token = json["token"]
    reporting_units = json["reporting_units"]
else:
    print("Error: " + str(result["status"]) + " - " + repr(result["text"]))

print(" <<< Token: " + token)


component = "sdc-questionnaires"
url = "https://" + component + ".herokuapp.com"
# url = "http://localhost:5001"
print("\n\n *** Testing " + component + " at " + url)


# Display the data we'll be working with

for reporting_unit in reporting_units:
    print(" --- RU " + dumps(reporting_unit))


# Questionnaires for the respondent unit

uri = "/questionnaires"
if len(reporting_units) > 0:
    print("\n --- " + uri + " ---")
    reference = reporting_units[0]["reference"]
    print(" >>> RU ref: " + repr(reference))
    parameters = {"reference": reference}
    result = get(url + uri, parameters=parameters, headers={"token": token})
    if result["status"] == 200:
        json = result["json"]
        token = json["token"]
        print(" <<< Token: " + token)
        content = get_json(token)
        print("Token content: " + dumps(content, sort_keys=True, indent=4, separators=(',', ': ')))
        questionnaires = json["questionnaires"]
        print(" <<< " + str(len(questionnaires)) + " result(s): " + repr(questionnaires))
    else:
        print("Error: " + str(result["status"]) + " - " + repr(result["text"]))
else:
    print(" * No respondent unit to query.")

