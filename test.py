import requests
from json import loads, dumps
from decoder import get_json
import unittest
from app import app
from jose import jwt
from jwt import encode, JWT_ALGORITHM

login_url = "https://sdc-login-user.herokuapp.com/login"
organisations_url = "https://sdc-organisations.herokuapp.com/reporting_units"

# Email address options
# email = "florence.nightingale@example.com"
# email = "chief.boyce@example.com"
email = "fireman.sam@example.com"
# email = "rob.dabank@example.com"

ok = 200
unauthorized = 401

valid_token = None
reporting_units = None


class ComponentTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_should_return_unauthorized_for_no_token(self):

        # Given
        # A request with no "token" header

        # When
        # We try to get reporting units
        response = self.app.get("/questionnaires")

        # Then
        # We should get a bad request status code
        self.assertEqual(response.status_code, unauthorized)

    def test_should_return_unauthorized_for_invalid_token(self):

        # Given
        # An invalid token
        token = jwt.encode({"respondent_id": "111"}, "wrong key", algorithm=JWT_ALGORITHM)

        # When
        # We try to get reporting units with the token
        response = self.app.get("/questionnaires", headers={"token": token})

        # Then
        # We should get an unauthorized status code
        self.assertEqual(response.status_code, unauthorized)

    def test_should_return_reporting_units_for_valid_token(self):
        global reporting_units
        print(reporting_units)

        # Given
        # A valid token and a valid reporting unit
        token = valid_token
        self.assertTrue(len(reporting_units) > 0)
        reporting_unit = reporting_units[0]

        # When
        # We try to get reporting units with the token
        response = self.app.get("/questionnaires",
                                headers={"token": token},
                                query_string={"reference": reporting_unit["reference"]})

        # Then
        # The questionnaires we get back should be for the specified reporting unit.
        self.assertEqual(response.status_code, ok)
        string = response.data.decode()
        json = loads(string)
        self.assertTrue("questionnaires" in json)
        questionnaires = json["questionnaires"]
        self.assertTrue(len(questionnaires) > 0)
        for questionnaire in json["questionnaires"]:
            print(questionnaire)
            self.assertTrue("reporting_unit" in questionnaire)
            self.assertEqual(reporting_unit["reference"], questionnaire["reporting_unit"])


def process(response):
    if response.status_code < 400:
        return {
            "status": response.status_code,
            "json": response.json()
        }
    else:
        return {
            "status": response.status_code,
            "text": response.text
        }


def get(url, parameters=None, headers=None):
    if parameters is None:
        parameters = {}
    if headers is None:
        headers = {}
    response = requests.get(url, params=parameters, headers=headers)
    return process(response)


def post(url, json, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    response = requests.post(url, data=json, headers=headers)
    return process(response)


def log_in():
    global valid_token
    # Account login
    print(" >>> Logging in and collecting tokens... (" + login_url + ")")
    message = {"email": email}
    result = post(login_url, dumps(message))
    if result["status"] == 200:
        json = result["json"]
        valid_token = json["token"]
    else:
        print("Error: " + str(result["status"]) + " - " + repr(result["text"]))
    print(" <<< Token      : " + repr(valid_token))


def get_reporting_units():
    global valid_token
    global reporting_units

    # Reporting units and survey permissions
    print(" >>> Getting reporting units and survey permissions... (" + organisations_url + ")")
    message = {"email": email}
    result = get(organisations_url, headers={"token": valid_token})
    if result["status"] == 200:
        json = result["json"]
        valid_token = json["token"]
        data = json["data"]
        reporting_units = data["reporting_units"]
    else:
        print("Error: " + str(result["status"]) + " - " + repr(result["text"]))
    print(" <<< Token      : " + valid_token)
    print(" <<< Reporting units: " + repr(reporting_units))


if __name__ == '__main__':
    log_in()
    get_reporting_units()
    unittest.main()


