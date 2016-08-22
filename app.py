import os
from flask import Flask, request, jsonify
from jwt import encode, decode
from jose.exceptions import JWSError


app = Flask(__name__)

questionnaires = [
    {
        "response_id": "801",
        "name": "Monthly Commodities Inquiry",
        "survey_id": "023",
        "form_type": "0203",
        "period": "0816",
        "respondent_unit": "222"
    },
    {
        "response_id": "802",
        "name": "Monthly Commodities Inquiry",
        "survey_id": "023",
        "form_type": "0203",
        "period": "0816",
        "respondent_unit": "223"
    },
    {
        "response_id": "803",
        "name": "Monthly Commodities Inquiry",
        "survey_id": "023",
        "form_type": "0203",
        "period": "0816",
        "respondent_unit": "224"
    },
    {
        "response_id": "804",
        "name": "Retail Sales Inquiry",
        "survey_id": "023",
        "form_type": "0102",
        "period": "0816",
        "respondent_unit": "222"
    },
    {
        "response_id": "805",
        "name": "Retail Sales Inquiry",
        "survey_id": "023",
        "form_type": "0102",
        "period": "0816",
        "respondent_unit": "223"
    },
    {
        "response_id": "806",
        "name": "Retail Sales Inquiry",
        "survey_id": "023",
        "form_type": "0102",
        "period": "0816",
        "respondent_unit": "224"
    }
]


@app.route('/', methods=['GET'])
def info():
    return """
        </ul>
            <li>Try POST to <a href="/login">/login</a> or <a href="/code">/code</a></li>
            <li>Valid email addresses are:
            florence.nightingale@example.com,
            chief.boyce@example.com,
            fireman.sam@example.com and
            rob.dabank@example.com
            </li>
            <li>Valid internet access codes are:
            abc123,
            def456,
            ghi789,
            jkl012,
            mno345 and
            pqr678
            </li>
            <li>Make a note of the returned token and pass it in a "token" header for other requests.</li>
            <li>Try GET or POST to <a href="/profile">/profile</a></li>
            <li>Then try GET to <a href="/respondent_units">/respondent_units</a> to see the RUs the respondent is associated with.</li>
            <li>Make a note of the expanded token</li>
            <li>Then try GET to
            <a href="/questionnaires">/questionnaires</a> and
            <a href="/respondents">/respondents</a>
            with a ?reference=... query parameter
            containing the RU ref to retrieve the lists of
            questionnaires and respondents associated with the specified RU</li>
        </ul>
        """


@app.route('/questionnaires', methods=['GET'])
def questionnaire_entries():
    token = request.headers.get("token")
    data = validate_token(token)
    reference = request.args.get('reference')
    # print(reference)
    # print(repr(data))

    if data and "respondent_id" in data and "respondent_units" in data:
        for respondent_unit in data["respondent_units"]:
            # print(respondent_unit["reference"] + " == " + reference)
            if respondent_unit["reference"] == reference:
                respondent_unit["questionnaires"] = []
                for questionnaire in questionnaires:
                    if questionnaire["respondent_unit"] == reference:
                        respondent_unit["questionnaires"].append(questionnaire)
                return jsonify({"questionnaires": respondent_unit["questionnaires"], "token": encode(data)})
            else:
                return unauthorized("Unable to find respondent unit for " + reference)
    return known_error("Please provide a 'token' header containing a JWT with a respondent_id value "
                       "and one or more respondent_unit entries "
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
