import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from jwt import encode, decode
from jose.exceptions import JWSError


app = Flask(__name__)
CORS(app)

questionnaires = [
    {
        "response_id": "801",
        "name": "Monthly Commodities Inquiry",
        "survey_id": "023",
        "form_type": "0203",
        "period": "0816",
        "reporting_unit": "222"
    },
    {
        "response_id": "802",
        "name": "Monthly Commodities Inquiry",
        "survey_id": "023",
        "form_type": "0203",
        "period": "0816",
        "reporting_unit": "223"
    },
    {
        "response_id": "803",
        "name": "Monthly Commodities Inquiry",
        "survey_id": "023",
        "form_type": "0203",
        "period": "0816",
        "reporting_unit": "224"
    },
    {
        "response_id": "804",
        "name": "Retail Sales Inquiry",
        "survey_id": "023",
        "form_type": "0102",
        "period": "0816",
        "reporting_unit": "222"
    },
    {
        "response_id": "805",
        "name": "Retail Sales Inquiry",
        "survey_id": "023",
        "form_type": "0102",
        "period": "0816",
        "reporting_unit": "223"
    },
    {
        "response_id": "806",
        "name": "Retail Sales Inquiry",
        "survey_id": "023",
        "form_type": "0102",
        "period": "0816",
        "reporting_unit": "224"
    }
]


@app.route('/', methods=['GET'])
def info():
    return """
        </ul>
            <li>Once you have obtained an expanded token from <a href="https://sdc-login-user.herokuapp.com/">https://sdc-login-user.herokuapp.com/</a>...</li>
            <li>Try GET to
            <a href="/questionnaires">/questionnaires</a>
            with a ?reference=... query parameter
            containing the RU ref to retrieve the list of
            questionnaires associated with the specified RU</li>
        </ul>
        """


@app.route('/questionnaires', methods=['GET'])
def questionnaire_entries():
    token = request.headers.get("token")
    data = validate_token(token)
    reference = request.args.get('reference')
    # print(reference)
    # print(repr(data))

    if data and "respondent_id" in data and "reporting_units" in data:
        for reporting_unit in data["reporting_units"]:
            # print(reporting_unit["reference"] + " == " + reference)
            if reporting_unit["reference"] == reference:
                reporting_unit["questionnaires"] = []
                for questionnaire in questionnaires:
                    if questionnaire["reporting_unit"] == reference:
                        reporting_unit["questionnaires"].append(questionnaire)
                return jsonify({"questionnaires": reporting_unit["questionnaires"], "token": encode(data)})
            else:
                return unauthorized("Unable to find respondent unit for " + reference)
    return known_error("Please provide a 'token' header containing a JWT with a respondent_id value "
                       "and one or more reporting_unit entries "
                       "and a query parameter 'reference' identifying the unit you wish to get questionnaires for.")


@app.errorhandler(401)
def unauthorized(error=None):
    app.logger.error("Unauthorized: '%s'", request.data.decode('UTF8'))
    message = {
        'status': 401,
        'message': "{}: {}".format(error, request.url),
    }
    resp = jsonify(message)
    resp.status_code = 401

    return resp


@app.errorhandler(400)
def known_error(error=None):
    app.logger.error("Bad request: '%s'", request.data.decode('UTF8'))
    message = {
        'status': 400,
        'message': "{}: {}".format(error, request.url),
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp


@app.errorhandler(500)
def unknown_error(error=None):
    app.logger.error("Error: '%s'", request.data.decode('UTF8'))
    message = {
        'status': 500,
        'message': "Internal server error: " + repr(error),
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


def validate_token(token):

    if token:
        try:
            return decode(token)
        except JWSError:
            return ""


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host='0.0.0.0', port=port)
