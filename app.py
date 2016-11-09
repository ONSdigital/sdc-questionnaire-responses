import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from jwt import encode, decode
from jose.exceptions import JWTError

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String

app = Flask(__name__)
CORS(app)

# Set up the database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI','sqlite:////tmp/sdc-questionnaire-responses.db')
db = SQLAlchemy(app)

# Survey model
class Survey(db.Model):
    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    survey_id = Column(String(3))
    period = Column(String(10))
    form_type = Column(String(4))
    reporting_unit = Column(String(20))
    reporting_unit_name = Column(String(105))


    def __init__(self, name=None, survey_id=None, period=None, form_type=None, reporting_unit=None, reporting_unit_name=None):
        self.name = name
        self.survey_id = survey_id
        self.period = period
        self.form_type = form_type
        self.reporting_unit = reporting_unit
        self.reporting_unit_name = reporting_unit_name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


def create_database():
    #db.drop_all()
    db.create_all()


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
    if data and "respondent_id" in data and "reporting_units" in data and reference:
        surveys = (db.session.query(Survey).filter(Survey.reporting_unit == reference).all())
        data['surveys'] = [su.as_dict() for su in surveys]
        token = encode(data)
        return jsonify({'data': data, 'token': token})
    return unauthorized("Please provide a 'token' header containing a valid JWT with respondent_id and reporting_units values.")


@app.route('/create-questionnaires', methods=['POST'])
def create_questionnaires():
    data = request.get_json()
    survey = Survey(data['survey_ref'], 'SURVEYID', data['survey_period'], data['form_type'],
                    data['reporting_unit'], data['reporting_unit_name'])
    db.session.add(survey)
    db.session.commit()
    return jsonify(survey.as_dict())


@app.errorhandler(401)
def unauthorized(error=None):
    app.logger.error("Unauthorized: '%s'", request.data.decode('UTF8'))
    message = {
        'message': "{}: {}".format(error, request.url),
    }
    resp = jsonify(message)
    resp.status_code = 401

    return resp


@app.errorhandler(400)
def known_error(error=None):
    app.logger.error("Bad request: '%s'", request.data.decode('UTF8'))
    message = {
        'message': "{}: {}".format(error, request.url),
    }
    resp = jsonify(message)
    resp.status_code = 400

    return resp


@app.errorhandler(500)
def unknown_error(error=None):
    app.logger.error("Error: '%s'", request.data.decode('UTF8'))
    message = {
        'message': "Internal server error: " + repr(error),
    }
    resp = jsonify(message)
    resp.status_code = 500

    return resp


def validate_token(token):

    if token:
        try:
            return decode(token)
        except JWTError:
            return ""


if __name__ == '__main__':

    # Create database
    create_database()

    # Start server
    port = int(os.environ.get("PORT", 5006))
    app.run(debug=True, host='0.0.0.0', port=port)
